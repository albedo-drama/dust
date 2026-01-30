from flask import Flask, request, redirect, url_for, render_template_string
import requests

app = Flask(__name__)

# --- KONFIGURASI API ---
API_BASE = "https://dramabos.asia/api/stardusttv"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- TEMPLATE HTML (FRONTEND) ---

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALBEDODUST-TV</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: sans-serif; }
        .glass { background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #06b6d4; border-radius: 3px; }
        /* Animasi loading gambar */
        .img-loading { background-color: #1e293b; animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <nav class="glass fixed w-full z-50 border-b border-slate-700 shadow-lg">
        <div class="container mx-auto px-4 py-3 flex justify-between items-center">
            <a href="/" class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 tracking-wider hover:opacity-80 transition">
                ALBEDODUST<span class="text-white text-sm ml-1 font-light">TV</span>
            </a>
            
            <form action="/search" method="get" class="flex items-center">
                <div class="relative">
                    <input type="text" name="q" placeholder="Cari judul..." value="{{ query if query else '' }}"
                           class="bg-slate-800 text-white pl-4 pr-10 py-1.5 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 border border-slate-600 transition w-32 md:w-64">
                    <button type="submit" class="absolute right-0 top-0 h-full px-3 text-slate-400 hover:text-cyan-400">
                        🔍
                    </button>
                </div>
            </form>
        </div>
    </nav>

    <main class="container mx-auto px-4 pt-24 flex-grow mb-10">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-slate-900/50 text-center py-8 border-t border-slate-800 text-slate-500 text-sm mt-auto">
        <p>&copy; 2026 ALBEDODUST-TV. <span class="text-cyan-600">Streaming Engine by Python.</span></p>
    </footer>
</body>
</html>
"""

HOME_TEMPLATE = """
{% extends "layout" %}
{% block content %}

{% if content.drama_populer and content.drama_populer|length > 0 %}
<div class="relative w-full h-64 md:h-[30rem] rounded-2xl overflow-hidden shadow-2xl shadow-cyan-900/20 mb-10 group border border-slate-700">
    {% set hero = content.drama_populer[0] %}
    <img src="/cover/{{ hero.vid }}" 
         class="w-full h-full object-cover opacity-60 group-hover:scale-105 transition duration-1000 img-loading"
         onload="this.classList.remove('img-loading')">
    
    <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/40 to-transparent flex items-end p-6 md:p-10">
        <div class="max-w-2xl relative z-10">
            <span class="bg-cyan-600 text-white text-[10px] md:text-xs font-bold px-2 py-1 rounded mb-3 inline-block tracking-widest uppercase">Paling Populer</span>
            <h1 class="text-3xl md:text-6xl font-black text-white mb-4 leading-tight drop-shadow-lg">{{ hero.title }}</h1>
            <a href="/drama/{{ hero.vid }}" class="inline-flex items-center bg-cyan-500 hover:bg-cyan-400 text-slate-900 px-6 py-2.5 rounded-full font-bold transition shadow-lg shadow-cyan-500/40 hover:shadow-cyan-400/60 transform hover:-translate-y-1">
                ▶ Mulai Nonton
            </a>
        </div>
    </div>
</div>
{% endif %}

{% macro render_grid(items, color_theme, badge_text=None) %}
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
    {% for item in items %}
    <a href="/drama/{{ item.vid }}" class="group relative block bg-slate-800 rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-{{ color_theme }}-500/10 border border-slate-700/50 hover:border-{{ color_theme }}-500/50">
        <div class="aspect-[3/4] bg-slate-800 relative overflow-hidden">
            <img src="{{ item.image if item.image else '/cover/' + item.vid }}" 
                 alt="{{ item.title }}" 
                 class="w-full h-full object-cover group-hover:scale-110 transition duration-500 img-loading"
                 loading="lazy"
                 onload="this.classList.remove('img-loading')">
            
            {% if badge_text %}
            <div class="absolute top-2 right-2 z-10">
                <span class="bg-{{ color_theme }}-600 text-[10px] font-bold px-2 py-0.5 rounded text-white shadow backdrop-blur-md bg-opacity-80">{{ badge_text }}</span>
            </div>
            {% endif %}

            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center backdrop-blur-[1px]">
                <div class="w-12 h-12 bg-{{ color_theme }}-500 rounded-full flex items-center justify-center shadow-lg text-white pl-1 scale-0 group-hover:scale-100 transition-transform duration-300">▶</div>
            </div>
        </div>
        <div class="p-3 bg-slate-800">
            <h3 class="text-sm font-semibold text-slate-200 line-clamp-1 group-hover:text-{{ color_theme }}-400 transition">{{ item.title }}</h3>
        </div>
    </a>
    {% endfor %}
</div>
{% endmacro %}

<div class="space-y-12">
    <section>
        <h2 class="text-xl font-bold text-white flex items-center gap-3 mb-5">
            <span class="w-1.5 h-6 bg-cyan-500 rounded-full shadow-[0_0_10px_#06b6d4]"></span> Drama Populer
        </h2>
        {{ render_grid(content.drama_populer, 'cyan') }}
    </section>

    <section>
        <h2 class="text-xl font-bold text-white flex items-center gap-3 mb-5">
            <span class="w-1.5 h-6 bg-purple-500 rounded-full shadow-[0_0_10px_#a855f7]"></span> Terbaru Dirilis
        </h2>
        {{ render_grid(content.terbaru_dirilis, 'purple', 'NEW') }}
    </section>

    <section>
        <h2 class="text-xl font-bold text-white flex items-center gap-3 mb-5">
            <span class="w-1.5 h-6 bg-emerald-500 rounded-full shadow-[0_0_10px_#10b981]"></span> Sedang Tayang
        </h2>
        {{ render_grid(content.sedang_tayang, 'emerald', 'ON GOING') }}
    </section>

    <section>
        <h2 class="text-xl font-bold text-white flex items-center gap-3 mb-5">
            <span class="w-1.5 h-6 bg-rose-500 rounded-full shadow-[0_0_10px_#f43f5e]"></span> Eksklusif
        </h2>
        {{ render_grid(content.eksklusif, 'rose', 'VIP') }}
    </section>
</div>
{% endblock %}
"""

SEARCH_TEMPLATE = """
{% extends "layout" %}
{% block content %}
<div class="mb-8 flex flex-col md:flex-row justify-between items-end gap-2 border-b border-slate-700 pb-4">
    <h2 class="text-2xl font-light">Hasil Pencarian: <span class="text-cyan-400 font-bold">"{{ query }}"</span></h2>
    {% if pagination.total %}
    <span class="text-sm text-slate-500 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">{{ pagination.total }} Drama Ditemukan</span>
    {% endif %}
</div>

{% if results %}
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-10">
    {% for item in results %}
    <a href="/drama/{{ item.id }}" class="group block bg-slate-800 rounded-xl overflow-hidden hover:scale-105 transition duration-300 border border-slate-700 hover:border-cyan-500 shadow-lg hover:shadow-cyan-900/30">
        <div class="aspect-[3/4] relative">
            <img src="{{ item.cover_path }}" alt="{{ item.english_name }}" class="w-full h-full object-cover img-loading" onload="this.classList.remove('img-loading')">
            <div class="absolute top-2 right-2 bg-slate-900/80 backdrop-blur text-cyan-400 text-[10px] font-bold px-2 py-1 rounded border border-cyan-500/30">
                {{ item.episode_total }} EPS
            </div>
            <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black via-black/70 to-transparent p-2 pt-6">
                 <p class="text-[10px] text-slate-300 flex items-center gap-1">
                    <span>🔥</span> {{ item.plays_num }}
                 </p>
            </div>
        </div>
        <div class="p-3">
            <h3 class="text-sm font-bold text-white line-clamp-1 group-hover:text-cyan-400 transition">{{ item.english_name }}</h3>
            <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ item.intro }}</p>
        </div>
    </a>
    {% endfor %}
</div>

{% if pagination.last_page > 1 %}
<div class="flex justify-center items-center gap-4">
    {% if pagination.current_page > 1 %}
    <a href="/search?q={{ query }}&page={{ pagination.current_page - 1 }}" 
       class="px-5 py-2 bg-slate-800 hover:bg-cyan-600 border border-slate-700 hover:border-cyan-500 text-white rounded-full transition flex items-center gap-2 group">
        <span class="group-hover:-translate-x-1 transition">&laquo;</span> Previous
    </a>
    {% else %}
    <span class="px-5 py-2 bg-slate-900 text-slate-700 rounded-full border border-slate-800 cursor-not-allowed">&laquo; Previous</span>
    {% endif %}

    <div class="bg-slate-900 px-6 py-2 rounded-full border border-slate-700 text-sm shadow-inner">
        Page <span class="text-cyan-400 font-bold">{{ pagination.current_page }}</span> / {{ pagination.last_page }}
    </div>

    {% if pagination.current_page < pagination.last_page %}
    <a href="/search?q={{ query }}&page={{ pagination.current_page + 1 }}" 
       class="px-5 py-2 bg-slate-800 hover:bg-cyan-600 border border-slate-700 hover:border-cyan-500 text-white rounded-full transition flex items-center gap-2 group">
        Next <span class="group-hover:translate-x-1 transition">&raquo;</span>
    </a>
    {% else %}
    <span class="px-5 py-2 bg-slate-900 text-slate-700 rounded-full border border-slate-800 cursor-not-allowed">Next &raquo;</span>
    {% endif %}
</div>
{% endif %}

{% else %}
<div class="flex flex-col items-center justify-center py-20 text-slate-600">
    <div class="text-6xl mb-4 opacity-50">📂</div>
    <p class="text-xl font-light">Tidak ada hasil untuk kata kunci ini.</p>
    <a href="/" class="mt-6 px-6 py-2 rounded-full bg-slate-800 text-cyan-500 hover:bg-slate-700 transition">Kembali ke Home</a>
</div>
{% endif %}
{% endblock %}
"""

WATCH_TEMPLATE = """
{% extends "layout" %}
{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
    
    <div class="lg:col-span-8 space-y-6">
        <div class="bg-black rounded-2xl overflow-hidden aspect-video relative shadow-2xl shadow-cyan-900/20 border border-slate-700 group ring-1 ring-slate-700">
            <video id="video" class="w-full h-full" controls autoplay poster="{{ video.snapshot_url }}"></video>
        </div>

        <div class="flex justify-between items-center bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50">
            {% if prev_ep %}
            <a href="/watch/{{ info.id }}/{{ prev_ep.id }}" class="flex items-center gap-2 text-slate-300 hover:text-cyan-400 transition text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-700">
                <span>⏮</span> Prev Ep
            </a>
            {% else %}
            <span class="text-slate-600 flex items-center gap-2 text-sm px-3 py-2">⏮ Prev Ep</span>
            {% endif %}

            <div class="text-center">
                <h2 class="text-cyan-400 font-bold text-lg tracking-wide line-clamp-1 px-2">{{ video.name }}</h2>
            </div>

            {% if next_ep %}
            <a href="/watch/{{ info.id }}/{{ next_ep.id }}" class="flex items-center gap-2 text-slate-900 bg-cyan-500 hover:bg-cyan-400 transition text-sm font-bold px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/20">
                Next Ep <span>⏭</span>
            </a>
            {% else %}
            <span class="text-slate-600 flex items-center gap-2 text-sm px-3 py-2">Next Ep ⏭</span>
            {% endif %}
        </div>

        <div class="bg-slate-800/30 rounded-2xl p-6 border border-slate-700/50">
            <h1 class="text-3xl font-bold text-white mb-3">{{ info.english_name }}</h1>
            
            <div class="flex flex-wrap gap-2 mb-4">
                <span class="bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded">Views: {{ info.plays_num }}</span>
                <span class="bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded">Total: {{ info.episode_total }} Eps</span>
                {% if info.labels %}
                    {% for label in info.labels %}
                    <span class="bg-cyan-900/50 text-cyan-300 text-xs px-2 py-1 rounded border border-cyan-800">{{ label.english_name }}</span>
                    {% endfor %}
                {% endif %}
            </div>

            <p class="text-slate-400 text-sm leading-relaxed border-l-2 border-slate-600 pl-4">
                {{ info.intro }}
            </p>
        </div>
    </div>

    <div class="lg:col-span-4 flex flex-col h-full max-h-[calc(100vh-100px)]">
        <div class="bg-slate-800 rounded-t-2xl p-4 border-b border-slate-700 flex justify-between items-center sticky top-0 z-10">
            <h3 class="font-bold text-white flex items-center gap-2">
                <span class="text-xl">📑</span> Daftar Episode
            </h3>
            <span class="text-xs text-slate-400">{{ episodes|length }} Episodes</span>
        </div>
        
        <div class="bg-slate-800/50 rounded-b-2xl p-2 overflow-y-auto custom-scroll flex-grow border border-t-0 border-slate-700">
            <div class="grid grid-cols-4 sm:grid-cols-5 lg:grid-cols-3 xl:grid-cols-4 gap-2 p-2">
                {% for ep in episodes %}
                <a href="/watch/{{ info.id }}/{{ ep.id }}" 
                   class="relative block text-center py-3 rounded-lg text-sm font-bold transition-all duration-200 border 
                   {% if ep.id == video.id %} 
                        bg-cyan-600 border-cyan-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.5)] scale-105 z-10
                   {% else %} 
                        bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600 hover:border-slate-500 hover:text-white
                   {% endif %}">
                   {{ ep.sort }}
                   {% if ep.id == video.id %}
                   <span class="absolute -top-1 -right-1 flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                    </span>
                   {% endif %}
                </a>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<script>
    var video = document.getElementById('video');
    var videoSrc = "{{ video.filepath }}";

    if (Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(videoSrc);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            video.play();
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = videoSrc;
        video.addEventListener('loadedmetadata', function() {
            video.play();
        });
    }
</script>
{% endblock %}
"""

# --- BACKEND LOGIC ---

def get_json(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Setup Jinja Loader
from jinja2 import DictLoader
app.jinja_env.loader = DictLoader({
    'layout': LAYOUT_TEMPLATE,
    'home': HOME_TEMPLATE,
    'search': SEARCH_TEMPLATE,
    'watch': WATCH_TEMPLATE
})

# --- ROUTES ---

@app.route('/')
def index():
    # Ambil data home yang (sayangnya) gambarnya kosong
    data = get_json(f"{API_BASE}/home")
    if data and data.get('status'):
        return render_template_string(HOME_TEMPLATE, content=data['data'])
    return "Gagal memuat API Home", 500

# [NEW] ROUTE KHUSUS UNTUK PROXY GAMBAR
@app.route('/cover/<vid>')
def get_cover_image(vid):
    # 1. Tembak API Episode/Detail pakai ID (vid)
    url = f"{API_BASE}/episodes/{vid}"
    data = get_json(url)
    
    # 2. Ambil cover_path yang ASLI
    if data and data.get('status') and 'video_info' in data.get('data', {}):
        cover_url = data['data']['video_info'].get('cover_path')
        if cover_url:
            # 3. Redirect browser ke gambar asli
            # Cache control penting biar gak nembak api terus menerus
            response = redirect(cover_url)
            response.headers['Cache-Control'] = 'public, max-age=3600' # Cache 1 jam
            return response
            
    # Fallback jika gagal
    return redirect("https://via.placeholder.com/300x400?text=No+Cover")

@app.route('/search')
def search():
    query = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('index'))
    
    data = get_json(f"{API_BASE}/search?q={query}&page={page}")
    results = []
    pagination = {}
    
    if data and data.get('status') and data.get('data'):
        results = data['data']['data']
        pagination = {
            'current_page': data['data']['current_page'],
            'last_page': data['data']['last_page'],
            'total': data['data']['total']
        }
    
    return render_template_string(SEARCH_TEMPLATE, results=results, query=query, pagination=pagination)

@app.route('/drama/<vid>')
def detail(vid):
    data = get_json(f"{API_BASE}/episodes/{vid}")
    if data and data.get('status') and data['data']['list']:
        first_ep_id = data['data']['list'][0]['id']
        return redirect(url_for('watch', vid=vid, epid=first_ep_id))
    return "Drama/Episode tidak ditemukan", 404

@app.route('/watch/<vid>/<int:epid>')
def watch(vid, epid):
    data = get_json(f"{API_BASE}/episodes/{vid}")
    
    if data and data.get('status'):
        episodes = data['data']['list']
        video_info = data['data']['video_info']
        
        current_ep = None
        prev_ep = None
        next_ep = None
        
        for i, ep in enumerate(episodes):
            if ep['id'] == epid:
                current_ep = ep
                if i > 0:
                    prev_ep = episodes[i-1]
                if i < len(episodes) - 1:
                    next_ep = episodes[i+1]
                break
        
        if current_ep:
            return render_template_string(WATCH_TEMPLATE, 
                                          video=current_ep, 
                                          info=video_info, 
                                          episodes=episodes,
                                          prev_ep=prev_ep,
                                          next_ep=next_ep)
    
    return "Error memuat player", 404

if __name__ == '__main__':
    app.run(debug=True)
