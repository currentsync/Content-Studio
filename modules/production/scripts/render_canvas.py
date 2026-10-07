#!/usr/bin/env python3
"""逐帧渲染：起本地 http 服务 → 无头 Chromium 打开 index.html → 对每帧调用 window.renderFrame(t)
→ 读 canvas 像素 → 管道送 ffmpeg 出 60fps mp4，最后混入音轨。

uv run --with playwright python modules/production/scripts/render_canvas.py --out ../成片/复刻_v1.mp4 [--audio ../音频/复刻音轨.wav] [--from 0 --to 片长] [--fps 60]
    [--film gallery]（读 eras_gallery.js）[--solo <id> --stills 0.2,0.6 --no-counter]
uv run --with playwright python modules/production/scripts/render_canvas.py --spec clip.json --out 片段.mp4 [--alpha] [--stills 0.5,2]
    参数化片段（口播管线的「动画段」，契约见 references/09）：时长严格 = spec.duration（帧数 round(duration×fps)），
    宽高/fps 从 spec 读；默认无声 H.264 yuv420p、每秒一个关键帧（GOP=fps，管线渲染器按秒 seek），--alpha 出 ProRes 4444 带透明（.mov）。spec 里图片路径相对 spec 文件。
页面里有 pageerror 或 console.error（场景报错、缺字形）→ 渲完后非零退出。
"""
import argparse, base64, hashlib, http.server, json, socketserver, subprocess, threading, functools, time, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
import yaml

ap = argparse.ArgumentParser()
ap.add_argument('--out')
ap.add_argument('--request', help='ProductionRequest YAML')
ap.add_argument('--preview', action='store_true', help='只输出一张代表帧 PNG')
ap.add_argument('--audio')
ap.add_argument('--fps', type=int, default=60)
ap.add_argument('--from', dest='t0', type=float, default=0)
ap.add_argument('--to', dest='t1', type=float, default=None, help='默认 = 段落表算出的片长 window.__total')
ap.add_argument('--stills', help='逗号分隔秒数：只导出这些时刻的 png 到 --out 目录')
ap.add_argument('--solo', help='只渲某个时代（时间为本段局部时间），配合 --stills 或 --from/--to')
ap.add_argument('--film', default='', help='片子名：读 eras_<名>.js（默认 eras.js）')
ap.add_argument('--no-counter', action='store_true', help='--solo 时不画角标')
ap.add_argument('--crf', type=int, default=14)
ap.add_argument('--spec', help='参数化片段 spec.json（走 clip.html，不读段落表）')
ap.add_argument('--alpha', action='store_true', help='--spec 时出 ProRes 4444 带透明（背景不画）')
a = ap.parse_args()

repo_root = Path(__file__).resolve().parents[3]
root = repo_root / 'modules' / 'production' / 'engines' / 'canvas'
project_root = None
if a.request:
    request_path = Path(a.request).resolve()
    request = yaml.safe_load(request_path.read_text(encoding='utf-8'))
    if not isinstance(request, dict) or request.get('record_type') != 'production_request':
        raise SystemExit('--request 必须是 ProductionRequest YAML')
    from modules.workflow.scripts.project_store import validate_record
    try:
        validate_record(request)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    project_id = request.get('project_id', '')
    if not project_id or any(ch not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for ch in project_id):
        raise SystemExit('ProductionRequest 的 project_id 无效')
    project_root = (repo_root / 'projects' / project_id).resolve()
    if not request_path.is_relative_to(project_root):
        raise SystemExit('ProductionRequest 必须位于其 projects/<project_id> 目录内')
    native = request.get('native_input') or {}
    output = request.get('output') or {}
    spec_ref = native.get('path') if isinstance(native, dict) else None
    output_ref = output.get('path') if isinstance(output, dict) else None
    if not spec_ref:
        raise SystemExit('ProductionRequest.native_input.path 缺失')
    spec_path = (project_root / spec_ref).resolve()
    if not spec_path.is_relative_to(project_root) or not spec_path.is_file():
        raise SystemExit('ProductionRequest spec 不存在或越出项目目录')
    expected_spec_digest = native.get('sha256')
    if expected_spec_digest and hashlib.sha256(spec_path.read_bytes()).hexdigest() != expected_spec_digest:
        raise SystemExit('ProductionRequest native_input.sha256 与实际文件不一致')
    a.spec = str(spec_path)
    if output_ref:
        out_path = (project_root / output_ref).resolve()
        if not out_path.is_relative_to(project_root):
            raise SystemExit('ProductionRequest 输出路径越出项目目录')
        a.out = str(out_path)
if not a.out:
    raise SystemExit('必须提供 --out 或带输出路径的 --request')
if a.preview and not a.stills:
    a.stills = '1.0'
    if not a.out.endswith(('.png', '.jpg', '.jpeg')):
        a.out = str(Path(a.out).with_suffix('')) + '-preview'

route_doc = json.loads((root / 'resource-map.json').read_text(encoding='utf-8'))
routes = sorted(route_doc['routes'], key=lambda item: len(item['prefix']), reverse=True)
spec = None
if a.spec:
    sp = Path(a.spec).resolve(); spec = json.loads(sp.read_text(encoding='utf-8-sig'))
    if not isinstance(spec, dict) or not isinstance(spec.get('cues', []), list):
        raise SystemExit('spec 必须是对象，cues 必须是列表')
    def ref(v):                                            # 本地图片 → /__file__/<绝对路径>（只服务 spec 里点名的文件）
        if not v: return v
        if isinstance(v, str) and v.startswith(('http:', 'https:')):
            if project_root: raise SystemExit('正式项目不能依赖未固定的远程图片；请登记并使用项目内素材')
            return v
        if isinstance(v, str) and v.startswith('data:'): return v
        if not isinstance(v, str): raise SystemExit('图片引用必须是项目相对路径、data URI 或演示模式远程URL')
        f = (sp.parent / v).resolve()
        if not f.exists(): raise SystemExit(f'spec 里的图片不存在：{v}（相对 {sp.parent}）')
        if project_root and not f.is_relative_to(project_root): raise SystemExit(f'ProductionRequest 图片引用越出项目目录：{v}')
        ALLOWED.add(str(f)); return '/__file__/' + urllib.parse.quote(str(f))
    ALLOWED = set()
    for q in spec.get('cues', []):
        if not isinstance(q, dict): raise SystemExit('每个 cue 必须是对象')
        if q.get('image'): q['image'] = ref(q['image'])
    if (spec.get('data') or {}).get('image'): spec['data']['image'] = ref(spec['data']['image'])
    if a.alpha: spec['alpha'] = True
    style_index = yaml.safe_load((repo_root / 'modules' / 'creative' / 'styles' / 'index.yaml').read_text(encoding='utf-8'))
    grammar = next((item for item in style_index.get('clip_grammars', []) if item.get('id') == spec.get('grammar')), None)
    if not grammar or grammar.get('status') != 'usable':
        raise SystemExit(f"未知或不可运行的语法：{spec.get('grammar')}")
    duration = spec.get('duration')
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise SystemExit('spec.duration 必须是正数')
    supported = set(grammar.get('cue_kinds', []))
    for index, cue in enumerate(spec.get('cues', [])):
        kind = cue.get('kind')
        if kind not in supported:
            raise SystemExit(f'cue[{index}] kind 未被语法 {spec["grammar"]} 声明：{kind}')
        at = cue.get('at')
        if not isinstance(at, (int, float)) or at < 0 or at > duration:
            raise SystemExit(f'cue[{index}] at 必须落在 0 到片段时长 {duration} 秒内')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if args and str(args[-2]) in {'404', '500'}:
            print('[http]', fmt % args)
    def translate_path(self, path):
        url_path = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if path.startswith('/__file__/'):
            f = urllib.parse.unquote(path[len('/__file__/'):].split('?')[0])
            return f if spec and f in ALLOWED else '/nonexistent'
        if '\\' in url_path or '..' in Path(url_path).parts:
            return '/nonexistent'
        for route in routes:
            prefix = route['prefix']
            if (route.get('exact') and url_path == prefix) or (not route.get('exact') and url_path.startswith(prefix)):
                base = (repo_root / route['path']).resolve()
                suffix = (url_path.lstrip('/') if route.get('preserve_url') else url_path[len(prefix):].lstrip('/')) if not route.get('exact') else ''
                mapped = (base / suffix).resolve() if suffix else base
                if mapped == base or mapped.is_relative_to(base):
                    if not mapped.exists():
                        print(f'[resource 404] {url_path} -> {mapped}')
                    return str(mapped)
                return '/nonexistent'
        relative = url_path.lstrip('/') or 'index.html'
        mapped = (root / relative).resolve()
        if mapped.is_relative_to(root):
            if not mapped.exists():
                print(f'[resource 404] {url_path} -> {mapped}')
            return str(mapped)
        return '/nonexistent'
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=str(root)))
srv.daemon_threads = True
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-web-security', '--enable-gpu-rasterization', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    errors = []
    pg.on('requestfailed', lambda req: print('[requestfailed]', req.url, req.failure))
    def on_console(m):
        if m.type in ('error', 'warning'): print('[page]', m.text)
        if m.type == 'error': errors.append(m.text)
    pg.on('console', on_console)
    pg.on('pageerror', lambda e: (print('[pageerror]', e), errors.append(str(e))))
    if spec:
        pg.set_viewport_size({'width': spec.get('width', 1920), 'height': spec.get('height', 1080)})
        pg.add_init_script('window.CLIP_SPEC = ' + json.dumps(spec, ensure_ascii=False) + ';')
        pg.goto(f'http://127.0.0.1:{port}/clip.html?render=1')
    else:
        pg.goto(f'http://127.0.0.1:{port}/index.html?render=1' + (f'&film={a.film}' if a.film else ''))
    try:
        pg.wait_for_function('window.__ready === true || !!window.__bootFailed', timeout=120000)
    except Exception:
        print('[diagnostic]', pg.evaluate("({ready:window.__ready, bootFailed:window.__bootFailed, hasU:!!window.U, onStage:typeof window.U?.onStage, hasMO:!!window.MO, scripts:[...document.scripts].map(s=>({src:s.src,loaded:!!s.dataset.loaded}))})"))
        raise
    bf = pg.evaluate('window.__bootFailed || null')
    if bf: raise SystemExit('场景加载失败，拒绝渲染：\n' + bf)
    if a.t1 is None: a.t1 = pg.evaluate('window.__total')
    if spec: a.fps = spec.get('fps', 30); a.t0 = 0; a.t1 = spec['duration']
    grab = '''async (t)=>{ await window.prepare(t); window.renderFrame(t); return window.__canvas.toDataURL('image/png').split(',')[1]; }'''
    if a.solo:
        grab = '''async (t)=>{ window.renderSolo(%s, t, {counter: %s}); return window.__canvas.toDataURL('image/png').split(',')[1]; }''' % (repr(a.solo), 'false' if a.no_counter else 'true')
    if a.stills:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for s in a.stills.split(','):
            (out / f't{float(s):06.2f}.png').write_bytes(base64.b64decode(pg.evaluate(grab, float(s))))
        print('stills ->', out)
    else:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        vid = a.out if not a.audio else a.out + '.noaudio.mp4'
        enc = ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16'] if (spec and a.alpha) else \
              ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart'] + \
              (['-g', str(a.fps), '-keyint_min', str(a.fps), '-sc_threshold', '0'] if spec else [])   # 片段要被管线的渲染器按秒 seek：每秒一个关键帧，否则冻帧
        if spec and a.alpha and not vid.endswith('.mov'): print('提示：ProRes 4444 一般用 .mov 容器')
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-c:v', 'png', '-i', '-'] + enc + [vid],
                              stdin=subprocess.PIPE)
        n0, n1 = round(a.t0 * a.fps), round(a.t1 * a.fps)
        st = time.time()
        for i in range(n0, n1):
            ff.stdin.write(base64.b64decode(pg.evaluate(grab, i / a.fps)))
            if (i - n0) % 60 == 0:
                print(f'{i}/{n1}  {time.time()-st:.0f}s', flush=True)
        ff.stdin.close(); ff.wait()
        if a.audio:
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', vid, '-ss', str(a.t0), '-t', str(a.t1 - a.t0), '-i', a.audio,
                            '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', a.out], check=True)
            Path(vid).unlink()
        print('done ->', a.out)
    b.close()
srv.shutdown()
if errors: raise SystemExit(f'❌ 页面报错 {len(errors)} 条（见上方 [page]/[pageerror]）')
