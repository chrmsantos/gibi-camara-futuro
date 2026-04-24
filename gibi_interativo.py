# -*- coding: utf-8 -*-
import base64
import os
import sys
from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image

# --- CONFIGURACOES ---
_DIR              = os.path.dirname(os.path.abspath(__file__))
PDF_INPUT         = os.path.join(_DIR, "gibi_estatico.pdf")
HTML_OUTPUT       = os.path.join(_DIR, "index.html")
SOUND_FLIP        = os.path.join(_DIR, "flip.mp3")
SOUND_BG          = os.path.join(_DIR, "background.mp3")
LARGURA_OTIMIZADA = 1280
POPPLER_PATH      = r"C:\Users\csantos\poppler\poppler-24.08.0\Library\bin"


def pdf_to_base64_images(pdf_path):
    print("[INFO] Convertendo PDF em imagens e otimizando...")
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    base64_list = []
    for i, img in enumerate(images):
        w_percent = LARGURA_OTIMIZADA / float(img.size[0])
        h_size    = int(img.size[1] * w_percent)
        img       = img.resize((LARGURA_OTIMIZADA, h_size), Image.Resampling.LANCZOS)
        buffered  = BytesIO()
        img.save(buffered, format="JPEG", quality=75, optimize=True)
        img_str   = base64.b64encode(buffered.getvalue()).decode()
        base64_list.append(f"data:image/jpeg;base64,{img_str}")
        print(f"  [OK] Pagina {i + 1} processada.")
    return base64_list


def file_to_base64(file_path):
    if not os.path.exists(file_path):
        print(f"  [AVISO] Audio nao encontrado: {os.path.basename(file_path)}")
        return ""
    with open(file_path, "rb") as f:
        return f"data:audio/mpeg;base64,{base64.b64encode(f.read()).decode()}"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
    <title>C&acirc;mara do Futuro - Santa B&aacute;rbara d'Oeste</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <style>
        html, body {
            width: 100vw; height: 100vh;
            margin: 0; padding: 0;
            background: #000;
            overflow: hidden;
            font-family: sans-serif;
            position: fixed;
        }
        #splash-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #1a1a1a; z-index: 9999;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            color: white; text-align: center;
            padding: 20px; box-sizing: border-box;
        }
        #start-btn {
            padding: 15px 40px; font-size: 18px; cursor: pointer;
            background: #0056b3; color: white; border: none;
            border-radius: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-weight: bold; transition: background 0.2s;
        }
        #start-btn:hover { background: #004494; }
        .swiper { width: 100%; height: 100%; }
        .swiper-slide {
            width: 100%; height: 100%;
            background: #000; box-sizing: border-box;
            overflow: hidden;
        }
        .swiper-slide img {
            width: 100%; height: 100%;
            object-fit: contain; display: block;
            touch-action: none;
            will-change: transform;
            transform-origin: center center;
            user-select: none;
        }
        #page-counter {
            position: fixed; bottom: 12px; left: 50%;
            transform: translateX(-50%); z-index: 6000;
            background: rgba(0,0,0,0.55); color: #fff;
            font-size: 13px; padding: 4px 14px;
            border-radius: 12px; display: none;
            pointer-events: none;
        }
        #music-btn {
            position: fixed; top: 15px; right: 15px; z-index: 6000;
            width: 44px; height: 44px; border-radius: 50%;
            background: rgba(0,0,0,0.6); border: 2px solid #fff;
            color: #fff; display: none;
            align-items: center; justify-content: center;
            cursor: pointer; font-size: 20px;
        }
    </style>
</head>
<body>
    <div id="splash-screen">
        <h2 style="margin-bottom: 20px;">C&acirc;mara do Futuro</h2>
        <button id="start-btn">COME&Ccedil;AR LEITURA</button>
        <p style="font-size: 12px; margin-top: 15px; opacity: 0.7;">Toque para ativar tela cheia e som</p>
    </div>

    <button id="music-btn">&#x1F50A;</button>
    <div id="page-counter"></div>

    <div class="swiper">
        <div class="swiper-wrapper">__SLIDES__</div>
    </div>

    <audio id="flip-sound" src="__SOUND_FLIP__" preload="auto"></audio>
    <audio id="bg-music"   src="__SOUND_BG__"   loop preload="auto"></audio>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        var splash      = document.getElementById('splash-screen');
        var startBtn    = document.getElementById('start-btn');
        var musicBtn    = document.getElementById('music-btn');
        var pageCounter = document.getElementById('page-counter');
        var bgMusic     = document.getElementById('bg-music');
        var flipSound   = document.getElementById('flip-sound');

        var swiper = new Swiper('.swiper', {
            speed: 400,
            slidesPerView: 1,
            spaceBetween: 0,
            observer: true,
            observeParents: true,
            resizeObserver: true,
            on: {
                slideChange: function() {
                    if (swiper.previousIndex !== undefined) {
                        resetZoom(swiper.slides[swiper.previousIndex]);
                    }
                    zoom.scale = 1; zoom.tx = 0; zoom.ty = 0;
                    swiper.allowTouchMove = true;
                    flipSound.currentTime = 0;
                    flipSound.play().catch(function() {});
                    pageCounter.textContent = (swiper.activeIndex + 1) + ' / ' + swiper.slides.length;
                }
            }
        });

        function enterFullScreen() {
            var el = document.documentElement;
            var fn = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
            if (fn) return fn.call(el);
            return Promise.resolve();
        }

        startBtn.addEventListener('click', function() {
            enterFullScreen().catch(function() {});
            bgMusic.volume = 0.2;
            bgMusic.play().catch(function() {});
            splash.style.display = 'none';
            musicBtn.style.display = 'flex';
            pageCounter.style.display = 'block';
            pageCounter.textContent = '1 / ' + swiper.slides.length;
            swiper.update();
        });

        musicBtn.addEventListener('click', function() {
            if (bgMusic.paused) {
                bgMusic.play();
                musicBtn.innerHTML = '&#x1F50A;';
            } else {
                bgMusic.pause();
                musicBtn.innerHTML = '&#x1F507;';
            }
        });

        // --- ZOOM & PAN ---
        var MIN_SCALE = 1, MAX_SCALE = 4;
        var zoom = { scale: 1, tx: 0, ty: 0, lastScale: 1, lastTX: 0, lastTY: 0,
                     pinching: false, panning: false,
                     startDist: 0, startMidX: 0, startMidY: 0,
                     panStartX: 0, panStartY: 0 };

        function getActiveImg() {
            return swiper.slides[swiper.activeIndex]
                   && swiper.slides[swiper.activeIndex].querySelector('img');
        }
        function applyTransform(img) {
            img.style.transform = 'translate(' + zoom.tx + 'px,' + zoom.ty + 'px) scale(' + zoom.scale + ')';
        }
        function resetZoom(slideEl) {
            if (!slideEl) return;
            var img = slideEl.querySelector('img');
            if (img) img.style.transform = '';
        }
        function clamp(img) {
            var maxTX = img.offsetWidth  * (zoom.scale - 1) / 2;
            var maxTY = img.offsetHeight * (zoom.scale - 1) / 2;
            zoom.tx = Math.max(-maxTX, Math.min(maxTX, zoom.tx));
            zoom.ty = Math.max(-maxTY, Math.min(maxTY, zoom.ty));
        }
        function touchDist(a, b) {
            return Math.sqrt(Math.pow(a.clientX - b.clientX, 2) + Math.pow(a.clientY - b.clientY, 2));
        }
        function midpoint(a, b) {
            return { x: (a.clientX + b.clientX) / 2, y: (a.clientY + b.clientY) / 2 };
        }

        document.addEventListener('touchstart', function(e) {
            var img = getActiveImg(); if (!img) return;
            if (e.touches.length === 2) {
                zoom.pinching  = true;  zoom.panning = false;
                zoom.startDist = touchDist(e.touches[0], e.touches[1]);
                var m = midpoint(e.touches[0], e.touches[1]);
                zoom.startMidX = m.x; zoom.startMidY = m.y;
                zoom.lastScale = zoom.scale;
                zoom.lastTX    = zoom.tx; zoom.lastTY = zoom.ty;
                e.preventDefault();
            } else if (e.touches.length === 1 && zoom.scale > 1) {
                zoom.panning   = true;  zoom.pinching = false;
                zoom.panStartX = e.touches[0].clientX - zoom.tx;
                zoom.panStartY = e.touches[0].clientY - zoom.ty;
                e.preventDefault();
            }
        }, { passive: false });

        document.addEventListener('touchmove', function(e) {
            var img = getActiveImg(); if (!img) return;
            if (zoom.pinching && e.touches.length === 2) {
                var dist  = touchDist(e.touches[0], e.touches[1]);
                zoom.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, zoom.lastScale * (dist / zoom.startDist)));
                var m = midpoint(e.touches[0], e.touches[1]);
                zoom.tx = zoom.lastTX + (m.x - zoom.startMidX);
                zoom.ty = zoom.lastTY + (m.y - zoom.startMidY);
                clamp(img);
                swiper.allowTouchMove = zoom.scale <= 1;
                applyTransform(img);
                e.preventDefault();
            } else if (zoom.panning && e.touches.length === 1 && zoom.scale > 1) {
                zoom.tx = e.touches[0].clientX - zoom.panStartX;
                zoom.ty = e.touches[0].clientY - zoom.panStartY;
                clamp(img);
                applyTransform(img);
                e.preventDefault();
            }
        }, { passive: false });

        document.addEventListener('touchend', function(e) {
            if (e.touches.length < 2) zoom.pinching = false;
            if (e.touches.length === 0) {
                zoom.panning = false;
                if (zoom.scale < 1.05) {
                    zoom.scale = 1; zoom.tx = 0; zoom.ty = 0;
                    var img = getActiveImg();
                    if (img) applyTransform(img);
                    swiper.allowTouchMove = true;
                }
            }
        });

        // Ctrl + scroll no desktop
        document.addEventListener('wheel', function(e) {
            if (!e.ctrlKey) return;
            e.preventDefault();
            var img = getActiveImg(); if (!img) return;
            zoom.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, zoom.scale + (e.deltaY > 0 ? -0.15 : 0.15)));
            if (zoom.scale <= 1) { zoom.scale = 1; zoom.tx = 0; zoom.ty = 0; }
            clamp(img);
            applyTransform(img);
            swiper.allowTouchMove = zoom.scale <= 1;
        }, { passive: false });
    </script>
</body>
</html>"""


# --- EXECUCAO ---
try:
    if not os.path.exists(PDF_INPUT):
        print(f"[ERRO] PDF nao encontrado: {PDF_INPUT}")
        sys.exit(1)

    imgs_b64 = pdf_to_base64_images(PDF_INPUT)
    flip_b64 = file_to_base64(SOUND_FLIP)
    bg_b64   = file_to_base64(SOUND_BG)

    slides_html = "".join(
        f'<div class="swiper-slide"><img src="{img}" loading="lazy"></div>\n'
        for img in imgs_b64
    )

    final_html = (
        HTML_TEMPLATE
        .replace("__SLIDES__",     slides_html)
        .replace("__SOUND_FLIP__", flip_b64)
        .replace("__SOUND_BG__",   bg_b64)
    )

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"\n[SUCESSO] '{HTML_OUTPUT}' gerado ({len(imgs_b64)} paginas).")

except Exception as e:
    print(f"[ERRO] {e}")
    sys.exit(1)