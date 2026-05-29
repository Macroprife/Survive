// ===== animations.js - Pixel Art Canvas Animations =====

const PixelAnim = (() => {
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    const W = 400, H = 300;
    const PX = 4; // pixel scale
    ctx.imageSmoothingEnabled = false;

    // Color palette
    const C = {
        bg: '#0d0d1a',
        wall: '#2a2a3e', wallLight: '#3a3a5e',
        floor: '#1e1e30', floorLight: '#2e2e40',
        skin: '#d4a574', skinDark: '#b08050',
        hair: '#4a3728',
        shirt: '#5a7a5a', shirtDark: '#3a5a3a',
        pants: '#4a4a6a',
        fire1: '#ff4400', fire2: '#ff8800', fire3: '#ffcc00',
        fireGlow: 'rgba(255,100,0,0.15)',
        rain: '#6688cc',
        sand: '#ccaa66',
        blood: '#cc2200',
        green: '#39ff14',
        amber: '#ffbf00',
    };

    let currentScene = 'shelter';
    let frame = 0;
    let animTimer = null;
    let particles = [];
    let combatFlash = 0;
    let transitionAlpha = 0;
    let transitionTarget = 0;
    let transitionCallback = null;

    // ===== DRAWING PRIMITIVES =====
    function px(x, y, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x * PX, y * PX, PX, PX);
    }

    function rect(x, y, w, h, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x * PX, y * PX, w * PX, h * PX);
    }

    // ===== CHARACTER (16x16 grid, drawn at center-bottom) =====
    function drawCharacter(cx, cy) {
        const f = frame % 4;
        const breathe = f < 2 ? 0 : -1; // subtle vertical shift
        const bx = cx, by = cy + breathe;

        // Hair
        rect(bx-1, by-8, 4, 2, C.hair);
        // Head
        rect(bx-1, by-6, 4, 4, C.skin);
        // Eyes
        px(bx, by-5, '#222');
        px(bx+2, by-5, '#222');
        // Body
        rect(bx-1, by-2, 4, 3, C.shirt);
        rect(bx, by-2, 2, 3, C.shirtDark); // shirt detail
        // Arms - slight movement
        const armOff = f % 2 === 0 ? 0 : 1;
        px(bx-2, by-1 - armOff, C.skin);
        px(bx+3, by-1 - armOff, C.skin);
        // Legs
        rect(bx, by+1, 1, 2, C.pants);
        rect(bx+1, by+1, 1, 2, C.pants);
    }

    // ===== CAMPFIRE =====
    function drawCampfire(cx, cy) {
        const f = frame % 4;
        // Logs
        rect(cx-2, cy, 5, 1, '#5a3a1a');
        rect(cx-1, cy-1, 3, 1, '#4a2a0a');
        // Stones around
        px(cx-3, cy+1, '#555');
        px(cx+3, cy+1, '#555');
        px(cx-3, cy, '#444');
        px(cx+3, cy, '#444');

        // Glow
        ctx.fillStyle = C.fireGlow;
        ctx.beginPath();
        ctx.arc((cx+0.5)*PX, (cy-1)*PX, 20, 0, Math.PI*2);
        ctx.fill();

        // Flames - 4 frames
        const flames = [
            [[0,-1],[0,-2],[1,-2],[1,-3],[-1,-2]],
            [[0,-1],[0,-2],[1,-3],[1,-2],[-1,-2],[-1,-3]],
            [[0,-1],[0,-2],[0,-3],[1,-2],[-1,-2]],
            [[0,-1],[1,-2],[0,-2],[-1,-3],[0,-3]],
        ];
        const colors = [C.fire1, C.fire2, C.fire3];
        flames[f].forEach((p, i) => {
            px(cx + p[0], cy + p[1], colors[i % 3]);
        });
        // Ember
        if (f === 1) px(cx+2, cy-4, C.fire3);
        if (f === 3) px(cx-2, cy-4, C.fire2);
    }

    // ===== RAIN EFFECT =====
    function initRain() {
        particles = [];
        for (let i = 0; i < 60; i++) {
            particles.push({
                x: Math.random() * (W / PX),
                y: Math.random() * (H / PX),
                speed: 2 + Math.random() * 3,
            });
        }
    }

    function drawRain() {
        particles.forEach(p => {
            px(Math.floor(p.x), Math.floor(p.y), C.rain);
            p.y += p.speed;
            p.x += 0.3;
            if (p.y > H / PX) { p.y = -2; p.x = Math.random() * (W / PX); }
            if (p.x > W / PX) p.x = 0;
        });
    }

    // ===== SANDSTORM EFFECT =====
    function initSandstorm() {
        particles = [];
        for (let i = 0; i < 80; i++) {
            particles.push({
                x: Math.random() * (W / PX),
                y: Math.random() * (H / PX),
                speed: 1 + Math.random() * 4,
                size: Math.random() > 0.7 ? 2 : 1,
            });
        }
    }

    function drawSandstorm() {
        particles.forEach(p => {
            const alpha = 0.4 + Math.random() * 0.4;
            ctx.fillStyle = `rgba(204,170,102,${alpha})`;
            ctx.fillRect(p.x * PX, p.y * PX, p.size * PX, PX);
            p.x += p.speed;
            p.y += (Math.random() - 0.4) * 0.5;
            if (p.x > W / PX + 5) { p.x = -5; p.y = Math.random() * (H / PX); }
        });
    }

    // ===== LOCATION SCENES =====
    function drawShelterScene() {
        // Walls
        rect(0, 0, 100, 20, C.wall);
        rect(0, 0, 100, 2, C.wallLight);
        // Floor
        rect(0, 55, 100, 20, C.floor);
        // Floor tiles
        for (let i = 0; i < 100; i += 6) {
            rect(i, 58, 1, 1, C.floorLight);
        }
        // Window
        rect(10, 8, 12, 10, '#1a2a4a');
        rect(10, 8, 12, 1, '#555');
        rect(15, 8, 2, 10, '#555');
        // Shelves
        rect(70, 10, 20, 2, '#5a4a3a');
        rect(70, 18, 20, 2, '#5a4a3a');
        // Items on shelf
        rect(72, 8, 3, 2, '#6a6a5a');
        rect(78, 8, 2, 2, '#8a6a4a');
        // Rug
        rect(25, 55, 20, 3, '#5a3030');
    }

    function drawRuinedSupermarket() {
        // Ceiling with holes
        rect(0, 0, 100, 15, '#3a3a3a');
        rect(30, 0, 10, 15, '#1a1a2e'); // hole
        rect(60, 0, 8, 15, '#1a1a2e');
        // Floor - cracked
        rect(0, 55, 100, 20, '#3a3a3a');
        for (let i = 0; i < 8; i++) {
            const x = 5 + i * 12;
            rect(x, 56, 1, 8, '#2a2a2a');
        }
        // Shelves (some broken)
        rect(5, 20, 15, 30, '#5a4a3a');
        rect(5, 22, 15, 2, '#4a3a2a');
        rect(5, 30, 15, 2, '#4a3a2a');
        // Fallen shelf
        rect(30, 45, 25, 3, '#5a4a3a');
        // Debris
        rect(65, 50, 3, 2, '#6a6a6a');
        rect(70, 52, 2, 1, '#7a6a5a');
        // Scattered items
        px(10, 50, '#8a7a5a');
        px(40, 44, '#6a8a6a');
    }

    function drawHospitalCorridor() {
        // Walls - sterile white/green
        rect(0, 0, 100, 50, '#d0d8d0');
        rect(0, 0, 100, 3, '#a0b0a0');
        // Floor - tiles
        rect(0, 55, 100, 20, '#b0b8b0');
        for (let i = 0; i < 100; i += 10) {
            rect(i, 55, 1, 20, '#a0a8a0');
        }
        // Doors
        rect(10, 15, 14, 35, '#8a9a8a');
        rect(16, 15, 2, 35, '#6a7a6a'); // door line
        rect(60, 15, 14, 35, '#8a9a8a');
        // Overhead light (flickering)
        if (frame % 6 < 4) {
            rect(40, 2, 20, 2, '#f0f0e0');
            ctx.fillStyle = 'rgba(240,240,220,0.05)';
            ctx.fillRect(30*PX, 2*PX, 40*PX, 53*PX);
        }
        // Stretchers
        rect(30, 48, 20, 3, '#aaa');
        // Blood stain
        rect(45, 52, 4, 2, C.blood);
    }

    function drawWastelandScene() {
        // Sky
        rect(0, 0, 100, 25, '#4a3a2a');
        // Distant ruins
        rect(10, 10, 5, 15, '#3a3a3a');
        rect(18, 12, 3, 13, '#3a3a3a');
        rect(55, 8, 8, 17, '#3a3a3a');
        rect(65, 14, 4, 11, '#3a3a3a');
        // Ground
        rect(0, 40, 100, 35, '#5a4a30');
        // Cracked earth
        for (let i = 0; i < 15; i++) {
            const x = 3 + i * 7;
            rect(x, 42 + (i%3)*4, 3, 1, '#4a3a20');
        }
        // Dead tree
        rect(80, 20, 2, 20, '#4a3a2a');
        rect(77, 18, 3, 2, '#4a3a2a');
        rect(83, 16, 3, 2, '#4a3a2a');
        // Debris
        rect(30, 48, 4, 2, '#6a6a5a');
        rect(50, 46, 3, 3, '#7a6a5a');
    }

    const scenes = {
        shelter: drawShelterScene,
        supermarket: drawRuinedSupermarket,
        hospital: drawHospitalCorridor,
        wasteland: drawWastelandScene,
        outside: drawWastelandScene,
    };

    // ===== COMBAT FLASH =====
    function drawCombatFlash() {
        if (combatFlash > 0) {
            ctx.fillStyle = `rgba(255,50,50,${combatFlash * 0.15})`;
            ctx.fillRect(0, 0, W, H);
            combatFlash--;
        }
    }

    // ===== SCENE TRANSITION =====
    function drawTransition() {
        if (transitionAlpha > 0) {
            ctx.fillStyle = `rgba(0,0,0,${transitionAlpha})`;
            ctx.fillRect(0, 0, W, H);
            if (transitionTarget > 0) {
                transitionAlpha = Math.min(transitionAlpha + 0.08, 1);
                if (transitionAlpha >= 1 && transitionCallback) {
                    transitionCallback();
                    transitionCallback = null;
                    transitionTarget = -1;
                }
            } else {
                transitionAlpha = Math.max(transitionAlpha - 0.06, 0);
            }
        }
    }

    // ===== RENDER FRAME =====
    function render() {
        ctx.fillStyle = C.bg;
        ctx.fillRect(0, 0, W, H);

        // Draw scene background
        const drawScene = scenes[currentScene] || scenes.wasteland;
        drawScene();

        // Weather effects
        if (currentScene === 'outside' || currentScene === 'wasteland' || currentScene === 'supermarket') {
            if (currentScene === 'outside' || currentScene === 'wasteland') {
                // Randomly show rain or clear
                drawRain();
            }
        }

        // Campfire in shelter
        if (currentScene === 'shelter') {
            drawCampfire(30, 53);
        }

        // Character
        const charX = currentScene === 'shelter' ? 40 : 50;
        const charY = currentScene === 'hospital' ? 50 : (currentScene === 'supermarket' ? 48 : 53);
        drawCharacter(charX, charY);

        drawCombatFlash();
        drawTransition();

        frame++;
    }

    function startLoop() {
        if (animTimer) return;
        // Initialize rain by default
        initRain();
        animTimer = setInterval(render, 250); // ~4fps
    }

    function stopLoop() {
        if (animTimer) { clearInterval(animTimer); animTimer = null; }
    }

    // ===== PUBLIC API =====
    return {
        start: startLoop,
        stop: stopLoop,

        setScene(name) {
            const doSwitch = () => {
                currentScene = name;
                frame = 0;
                if (name === 'outside' || name === 'wasteland') initRain();
                if (name === 'sandstorm') { currentScene = 'wasteland'; initSandstorm(); }
                document.getElementById('scene-label').textContent = {
                    shelter: '庇护所',
                    supermarket: '废弃超市',
                    hospital: '医院走廊',
                    wasteland: '废土荒野',
                    outside: '废土荒野',
                }[name] || name;
            };
            transitionAlpha = 0.01;
            transitionTarget = 1;
            transitionCallback = doSwitch;
        },

        triggerCombatFlash() {
            combatFlash = 6;
        },

        triggerSandstorm() {
            initSandstorm();
        },
    };
})();
