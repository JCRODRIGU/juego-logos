import random
import string
import pandas as pd

def generar_sopa_logos_sonido_ok(df):
    # Detectar la columna producto (posición 9 / Columna J)
    columna = 'producto' if 'producto' in df.columns else df.columns[9] if len(df.columns) > 9 else df.columns[0]
    
    productos = df[columna].dropna().astype(str).tolist()
    
    # Extrae todas las palabras de la descripción que cumplan el largo
    palabras_totales = []
    for frase in productos:
        palabras_frase = frase.upper().replace(",", " ").split()
        for p in palabras_frase:
            limpia = p.replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")
            if 3 <= len(limpia) <= 10:
                palabras_totales.append(limpia)
    
    candidatas_unicas = list(set(palabras_totales))
    seleccionadas = random.sample(candidatas_unicas, min(15, len(candidatas_unicas)))
    
    TAMANO = 15
    matriz = [['' for _ in range(TAMANO)] for _ in range(TAMANO)]
    posiciones = {}

    for palabra in seleccionadas:
        colocada = False
        for _ in range(150):
            if colocada: break
            dir = random.choice(['H', 'V', 'D'])
            f, c = (random.randint(0, TAMANO-1), random.randint(0, TAMANO-len(palabra))) if dir == 'H' else \
                   (random.randint(0, TAMANO-len(palabra)), random.randint(0, TAMANO-1)) if dir == 'V' else \
                   (random.randint(0, TAMANO-len(palabra)), random.randint(0, TAMANO-len(palabra)))
            
            coords = []
            for i in range(len(palabra)):
                nf, nc = (f, c+i) if dir == 'H' else (f+i, c) if dir == 'V' else (f+i, c+i)
                coords.append(f"{nf}-{nc}")

            if all(matriz[int(p.split('-')[0])][int(p.split('-')[1])] in ('', palabra[i]) for i, p in enumerate(coords)):
                for i, p in enumerate(coords):
                    matriz[int(p.split('-')[0])][int(p.split('-')[1])] = palabra[i]
                posiciones[palabra] = coords
                colocada = True

    for f in range(TAMANO):
        for c in range(TAMANO):
            if matriz[f][c] == '': matriz[f][c] = random.choice(string.ascii_uppercase)

    matrix_js = str(matriz).replace("'", '"')
    words_pos_js = str(posiciones).replace("'", '"')
    botones_html = "".join([f'<span class="word-item" id="w-{w}">{w}</span>' for w in seleccionadas])

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Sopa Logos</title>
    <style>
        * { touch-action: none; user-select: none; -webkit-tap-highlight-color: transparent; }
        body { font-family: sans-serif; text-align: center; background: #fff; margin: 0; overflow: hidden; }
        .header { background: #2e7d32; color: white; padding: 10px; font-weight: bold; }
        
        /* CUADRADO ENVOLVENTE RECUPERADO (border) */
        #grid { 
            display: grid; grid-template-columns: repeat(15, 1fr); 
            width: 98vw; max-width: 450px; background: #444; gap: 1px; margin: 5px auto;
            border: 3px solid #2e7d32; /* Este es el cuadrado que mencionas */
        }
        
        .cell { 
            aspect-ratio: 1/1; background: white; display: flex; align-items: center; 
            justify-content: center; font-weight: bold; font-size: 16px; color: #000;
        }
        .sel { background: #fff176 !important; }
        .found { background: #4caf50 !important; color: white !important; }
        #word-list { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; padding: 10px; }
        .word-item { padding: 4px 8px; background: #eee; border-radius: 4px; font-size: 11px; border: 1px solid #ccc; }
        .word-found { background: #c8e6c9; color: #2e7d32; text-decoration: line-through; border-color: #2e7d32; }
        .win { display: none; background: #25D366; color: white; padding: 15px; border-radius: 30px; text-decoration: none; font-weight: bold; margin: 10px; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">LIBRERÍA LOGOS</div>
    <div id="grid"></div>
    <div id="word-list">__BOTONES__</div>
    <a href="https://wa.me/573125756581?text=Gane" id="win-btn" style="display:none" class="win">✅ RECLAMAR PREMIO</a>

    <script>
        const wordsPos = __WORDS_POS__;
        const matrix = __MATRIX__;
        let activeCoords = [];
        let foundCount = 0;
        let isSelecting = false;
        let audioCtx = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function playBeep(f, d) {
            if (!audioCtx) return;
            const o = audioCtx.createOscillator(); 
            const g = audioCtx.createGain();
            o.frequency.setValueAtTime(f, audioCtx.currentTime);
            o.type = 'sine';
            g.gain.setValueAtTime(0.1, audioCtx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + d);
            o.connect(g); 
            g.connect(audioCtx.destination); 
            o.start(); 
            o.stop(audioCtx.currentTime + d);
        }

        const grid = document.getElementById('grid');
        matrix.forEach((row, r) => row.forEach((char, c) => {
            const div = document.createElement('div');
            div.className = 'cell'; div.textContent = char;
            div.dataset.pos = r + '-' + c;
            grid.appendChild(div);
        }));

        function handleTouch(e) {
            const t = e.touches ? e.touches[0] : e;
            const el = document.elementFromPoint(t.clientX, t.clientY);
            if (el && el.classList.contains('cell')) {
                const pos = el.dataset.pos;
                if (!activeCoords.includes(pos)) {
                    activeCoords.push(pos);
                    el.classList.add('sel');
                    playBeep(440, 0.1); 
                    checkWords();
                }
            }
        }

        grid.addEventListener('touchstart', (e) => {
            initAudio(); 
            isSelecting = true;
            activeCoords = [];
            handleTouch(e);
        });

        grid.addEventListener('touchmove', (e) => {
            if (isSelecting) handleTouch(e);
        });

        window.addEventListener('touchend', () => {
            isSelecting = false;
            document.querySelectorAll('.sel').forEach(c => c.classList.remove('sel'));
            activeCoords = [];
        });

        function checkWords() {
            for (let word in wordsPos) {
                const coords = wordsPos[word];
                if (coords.every(p => {
                    const el = document.querySelector(`[data-pos="${p}"]`);
                    return el.classList.contains('sel') || el.classList.contains('found');
                })) {
                    coords.forEach(p => {
                        const el = document.querySelector(`[data-pos="${p}"]`);
                        el.classList.add('found');
                    });
                    const btn = document.getElementById('w-' + word);
                    if (btn && !btn.classList.contains('word-found')) {
                        btn.classList.add('word-found');
                        foundCount++;
                        playBeep(600, 0.4); 
                        if (foundCount === Object.keys(wordsPos).length) document.getElementById('win-btn').style.display = 'block';
                    }
                }
            }
        }
    </script>
</body>
</html>
    """
    final_html = html_template.replace("__BOTONES__", botones_html).replace("__WORDS_POS__", words_pos_js).replace("__MATRIX__", matrix_js)
    with open("index.html", "w", encoding="utf-8") as f: f.write(final_html)