// ===== game.js - Game Client Logic (fixed to match backend API) =====

const Game = (() => {
    const API_BASE = '/api';
    let gameId = null;
    let gameState = null;
    let actionInProgress = false;
    let itemRegistry = null;  // fetched from /api/items

    // ===== DOM REFS =====
    const narrative = document.getElementById('narrative-content');
    const narrativeArea = document.getElementById('narrative-area');
    const dayCounter = document.getElementById('day-counter');
    const overlayStart = document.getElementById('overlay-start');
    const overlayCraft = document.getElementById('overlay-craft');
    const overlaySave = document.getElementById('overlay-save');
    const overlayUseItem = document.getElementById('overlay-use-item');
    const overlayLocation = document.getElementById('overlay-location');

    const statBars = {
        hp: { bar: document.getElementById('bar-hp'), val: document.getElementById('val-hp') },
        hunger: { bar: document.getElementById('bar-hunger'), val: document.getElementById('val-hunger') },
        thirst: { bar: document.getElementById('bar-thirst'), val: document.getElementById('val-thirst') },
        energy: { bar: document.getElementById('bar-energy'), val: document.getElementById('val-energy') },
        sanity: { bar: document.getElementById('bar-sanity'), val: document.getElementById('val-sanity') },
    };

    // ===== API COMMUNICATION =====
    async function apiCall(method, path, body) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);
        try {
            const res = await fetch(`${API_BASE}${path}`, opts);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (e) {
            addNarrative(`[连接失败] ${e.message}`, 'danger');
            return null;
        }
    }

    // ===== NARRATIVE (TYPING EFFECT - SERIAL QUEUE) =====
    const _narrativeQueue = [];
    let _narrativeBusy = false;

    function _processQueue() {
        if (_narrativeBusy || _narrativeQueue.length === 0) return;
        _narrativeBusy = true;
        const { text, cls, resolve } = _narrativeQueue.shift();

        const line = document.createElement('div');
        line.className = `narrative-line ${cls}`;
        line.textContent = '';
        narrative.appendChild(line);
        narrativeArea.scrollTop = narrativeArea.scrollHeight;

        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                line.textContent += text[i];
                i++;
                narrativeArea.scrollTop = narrativeArea.scrollHeight;
            } else {
                clearInterval(interval);
                _narrativeBusy = false;
                resolve();
                _processQueue();
            }
        }, 20);
    }

    function addNarrative(text, cls = '') {
        return new Promise(resolve => {
            _narrativeQueue.push({ text, cls, resolve });
            _processQueue();
        });
    }

    function addNarrativeInstant(text, cls = '') {
        const line = document.createElement('div');
        line.className = `narrative-line ${cls}`;
        line.textContent = text;
        narrative.appendChild(line);
        narrativeArea.scrollTop = narrativeArea.scrollHeight;
    }

    function clearNarrative() {
        _narrativeQueue.length = 0;
        _narrativeBusy = false;
        narrative.innerHTML = '';
    }

    // ===== RENDER STATE =====
    function renderState(state) {
        if (!state) return;
        gameState = state;

        // Day counter
        dayCounter.textContent = `第 ${state.day || 1} 天`;

        // Stats - backend field is "player" not "player_stats"
        const stats = state.player || {};
        for (const key of ['hp', 'hunger', 'thirst', 'energy', 'sanity']) {
            const val = Math.max(0, Math.min(100, stats[key] || 0));
            if (statBars[key]) {
                statBars[key].bar.style.width = `${val}%`;
                statBars[key].val.textContent = val;
            }
        }

        // Inventory
        const invList = document.getElementById('inventory-list');
        const inv = state.inventory || [];
        if (inv.length === 0) {
            invList.innerHTML = '<div class="empty-inventory">背包空空如也...</div>';
        } else {
            invList.innerHTML = inv.map(item => {
                const name = item.name || item.id || '???';
                const qty = item.quantity ? ` x${item.quantity}` : '';
                const usable = itemRegistry ? (itemRegistry[item.id]?.usable ?? false) : item.usable;
                return `<div class="inv-item ${usable ? 'inv-item-usable' : ''}" data-item-id="${item.id}" ${usable ? `onclick="Game.useItem('${item.id}')"` : ''}>
                    <span>${name}${qty}</span>
                    ${usable ? '<span class="use-hint">[使用]</span>' : ''}
                </div>`;
            }).join('');
        }

        // Location-based scene - backend field is "current_location"
        const loc = state.current_location || 'shelter';
        const sceneMap = {
            shelter: 'shelter',
            supermarket: 'supermarket',
            hospital: 'hospital',
            police_station: 'wasteland',
            residential: 'wasteland',
            radio_tower: 'wasteland',
        };
        PixelAnim.setScene(sceneMap[loc] || 'wasteland');

        // Combat state: show/hide combat buttons
        const combatPanel = document.getElementById('combat-panel');
        if (state.pending_event && state.pending_event.type === 'combat') {
            combatPanel.classList.add('active');
            // Show combat info
            const effects = state.pending_event.effects || {};
            document.getElementById('combat-enemy-info').textContent =
                `${effects.enemy || '敌人'} (HP: ${effects.enemy_hp || '?'})`;
        } else {
            combatPanel.classList.remove('active');
        }

        // Game over check
        if (state.game_over) {
            disableActions(true);
            combatPanel.classList.remove('active');
            if (state.ending_reached) {
                addNarrative('═══════════════════════', 'event');
                addNarrative('🎉 你成功逃离了废土！', 'event');
                addNarrative(`存活天数: ${state.day}  |  得分: ${state.survival_score}`, 'event');
            } else {
                addNarrative('═══════════════════════', 'danger');
                addNarrative('你倒在了废土之中...', 'danger');
                addNarrative(`存活天数: ${state.day}  |  得分: ${state.survival_score}`, 'event');
            }
            // Show restart button
            addNarrative('', '');
            const restartDiv = document.createElement('div');
            restartDiv.className = 'narrative-line event';
            restartDiv.innerHTML = '<button class="restart-btn" onclick="location.reload()">🔄 重新开始</button>';
            narrative.appendChild(restartDiv);
        } else {
            disableActions(false);
        }

        // Location button label
        const locNames = {
            shelter: '庇护所', supermarket: '超市', hospital: '医院',
            police_station: '警察局', residential: '居民区', radio_tower: '通讯塔',
        };
        const locBtn = document.getElementById('btn-location');
        if (locBtn) locBtn.textContent = `📍 ${locNames[loc] || loc}`;
    }

    // ===== DISPLAY EVENTS FROM API =====
    function displayEvents(events) {
        if (!events || !Array.isArray(events)) return;
        events.forEach(ev => {
            if (!ev) return;
            // Backend event: {type, title, description, effects, choices, resolved}
            const cls = {
                combat: 'danger', combat_end: 'event', damage: 'danger',
                trap: 'danger', weather: 'danger', game_over: 'danger',
                loot: 'event', craft: 'event', use: 'event', equip: 'event',
                clue: 'event', victory: 'event', rest: 'info', move: 'info',
                daily: 'info', flee: 'info', sanity_break: 'danger',
                error: 'danger', inventory: 'info', narrative: '',
            }[ev.type] || '';

            if (ev.title && ev.description) {
                addNarrative(`【${ev.title}】`, cls);
                addNarrative(ev.description, cls);
            } else if (ev.description) {
                addNarrative(ev.description, cls);
            }

            // Combat flash
            if (ev.type === 'combat' || ev.type === 'combat_end') {
                PixelAnim.triggerCombatFlash();
            }
            // Weather effects
            if (ev.type === 'weather') {
                if (ev.title && (ev.title.includes('沙') || ev.title.includes('尘'))) {
                    PixelAnim.triggerSandstorm();
                }
            }
        });
    }

    // ===== ACTIONS =====
    async function doAction(actionType, extra = {}) {
        if (actionInProgress || !gameId) return;
        actionInProgress = true;
        disableActions(true);

        const actionLabels = {
            explore: '🔍 探索', rest: '💤 休息', craft: '🔧 合成',
            attack: '⚔️ 攻击', defend: '🛡️ 防御', flee: '🏃 逃跑',
            move: '📍 移动', use_item: '🎒 使用',
        };
        addNarrative(`> ${actionLabels[actionType] || actionType}...`, 'info');

        // Build request body matching backend Action model
        const body = {
            action_type: actionType,
            target: extra.target || null,
            item_id: extra.item_id || null,
            choice: extra.choice || null,
        };

        const data = await apiCall('POST', `/game/${gameId}/action`, body);

        if (data) {
            displayEvents(data.events);
            renderState(data.state);
        }

        actionInProgress = false;
        if (!gameState?.game_over) {
            disableActions(false);
        }
    }

    function disableActions(disabled) {
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.disabled = disabled;
        });
    }

    // ===== CRAFT MENU =====
    async function showCraftMenu() {
        const recipes = [
            { id: 'medicine', name: '草药药剂', materials: '草药 x1 + 水 x1', effect: 'HP +30' },
            { id: 'bandage', name: '消毒绷带', materials: '布料 x1 + 酒精 x1', effect: 'HP +20' },
            { id: 'weapon', name: '自制武器', materials: '金属 x2 + 木头 x1', effect: '攻击 +8' },
            { id: 'armor', name: '强化护甲', materials: '金属 x3 + 布料 x2', effect: '防御 12' },
            { id: 'torch', name: '火把', materials: '木头 x1 + 布料 x1', effect: '降低遭遇率' },
        ];

        const craftList = document.getElementById('craft-list');
        craftList.innerHTML = recipes.map(r => {
            return `<div class="craft-item">
                <span>${r.name} (${r.materials}) <span class="hint">${r.effect}</span></span>
                <button onclick="Game.craft('${r.id}')">合成</button>
            </div>`;
        }).join('');

        overlayCraft.classList.add('active');
    }

    // ===== LOCATION MENU =====
    function showLocationMenu() {
        const locations = [
            { id: 'shelter', name: '废弃避难所', danger: '安全' },
            { id: 'supermarket', name: '废弃超市', danger: '中等' },
            { id: 'hospital', name: '市中心医院', danger: '高' },
            { id: 'police_station', name: '警察局', danger: '高' },
            { id: 'residential', name: '居民区废墟', danger: '中等' },
            { id: 'radio_tower', name: '通讯塔', danger: '极高' },
        ];

        const locList = document.getElementById('location-list');
        locList.innerHTML = locations.map(loc => {
            const isCurrent = gameState && gameState.current_location === loc.id;
            const explored = gameState && gameState.explored_locations?.includes(loc.id);
            return `<div class="craft-item">
                <span>${loc.name} [${loc.danger}] ${isCurrent ? '← 当前' : ''} ${explored && !isCurrent ? '✓' : ''}</span>
                ${!isCurrent ? `<button onclick="Game.move('${loc.id}')">前往</button>` : ''}
            </div>`;
        }).join('');

        overlayLocation.classList.add('active');
    }

    // ===== USE ITEM MENU =====
    function showUseItemMenu() {
        if (!gameState) return;
        const inv = gameState.inventory || [];
        const usable = inv.filter(item => itemRegistry ? (itemRegistry[item.id]?.usable ?? false) : false);

        const useList = document.getElementById('use-item-list');
        if (usable.length === 0) {
            useList.innerHTML = '<div class="craft-item">没有可使用的物品</div>';
        } else {
            useList.innerHTML = usable.map(item => {
                const effect = itemRegistry?.[item.id]?.effect || '';
                return `<div class="craft-item">
                    <span>${item.name} x${item.quantity} ${effect ? `(${effect})` : ''}</span>
                    <button onclick="Game.useItem('${item.id}')">使用</button>
                </div>`;
            }).join('');
        }

        overlayUseItem.classList.add('active');
    }

    // ===== SAVE/LOAD =====
    async function saveGame() {
        if (!gameId) return;
        const data = await apiCall('POST', `/game/${gameId}/save`);
        if (data) {
            addNarrative(`[系统] ${data.message || '游戏已保存'}`, 'info');
        }
    }

    async function showSaves() {
        const data = await apiCall('GET', '/saves');
        const saves = Array.isArray(data) ? data : [];
        const saveList = document.getElementById('save-list');
        saveList.innerHTML = saves.length === 0
            ? '<div class="craft-item">暂无存档</div>'
            : saves.map(s => {
                return `<div class="craft-item">
                    <span>${s.save_name || s.save_id} (${s.saved_at?.split('T')[0] || ''})</span>
                    <button onclick="Game.loadSave('${s.save_id}')">加载</button>
                </div>`;
            }).join('');

        overlaySave.classList.add('active');
    }

    async function loadSave(saveId) {
        if (!itemRegistry) {
            const reg = await apiCall('GET', '/items');
            if (reg) itemRegistry = reg;
        }
        const data = await apiCall('POST', `/load/${saveId}`);
        if (data) {
            gameId = data.game_id;
            closeAllOverlays();
            clearNarrative();
            addNarrative('[系统] ' + (data.message || '存档已加载'), 'info');
            renderState(data.state);
            PixelAnim.start();
            disableActions(false);
        }
    }

    // ===== NEW GAME =====
    async function newGame() {
        if (!itemRegistry) {
            const reg = await apiCall('GET', '/items');
            if (reg) itemRegistry = reg;
        }
        const data = await apiCall('POST', '/new-game');
        if (data) {
            gameId = data.game_id;
            closeAllOverlays();
            clearNarrative();

            // Display initial narrative event
            if (data.state?.events_log?.length > 0) {
                displayEvents(data.state.events_log);
            } else {
                addNarrative('你睁开双眼，废墟的尘埃在阳光中飞舞。');
                addNarrative('一个破旧的庇护所，勉强能遮风挡雨。');
                addNarrative('你决定...活下去。', 'event');
            }

            renderState(data.state);
            PixelAnim.start();
            disableActions(false);
        }
    }

    // ===== HELPERS =====
    function closeAllOverlays() {
        document.querySelectorAll('.overlay').forEach(o => o.classList.remove('active'));
    }

    // ===== EVENT LISTENERS =====
    document.getElementById('btn-new-game').addEventListener('click', newGame);
    document.getElementById('btn-load-game').addEventListener('click', showSaves);
    document.getElementById('btn-help').addEventListener('click', () => {
        document.getElementById('overlay-help').classList.add('active');
    });

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'explore') doAction('explore');
            else if (action === 'rest') doAction('rest');
            else if (action === 'craft') showCraftMenu();
            else if (action === 'inventory') showUseItemMenu();
            else if (action === 'move') showLocationMenu();
            else if (action === 'save') saveGame();
        });
    });

    document.querySelectorAll('.overlay-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.close;
            if (target) document.getElementById(target)?.classList.remove('active');
            else btn.closest('.overlay')?.classList.remove('active');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (overlayStart.classList.contains('active')) return;
        // Don't trigger shortcuts if an overlay is open
        const anyOverlay = document.querySelector('.overlay.active:not(#overlay-start)');
        if (anyOverlay && e.key !== 'Escape') return;

        switch (e.key) {
            case 'Escape': closeAllOverlays(); break;
            case '1': case 'e': doAction('explore'); break;
            case '2': case 'r': doAction('rest'); break;
            case '3': case 'c': showCraftMenu(); break;
            case '4': case 'i': showUseItemMenu(); break;
            case '5': case 'm': showLocationMenu(); break;
            case 's': if (e.ctrlKey) { e.preventDefault(); saveGame(); } break;
            case 'h': case '?': document.getElementById('overlay-help').classList.toggle('active'); break;
            // Combat shortcuts
            case 'a': if (gameState?.pending_event?.type === 'combat') doAction('attack'); break;
            case 'd': if (gameState?.pending_event?.type === 'combat') doAction('defend'); break;
            case 'f': if (gameState?.pending_event?.type === 'combat') doAction('flee'); break;
        }
    });

    // ===== PUBLIC API =====
    return {
        craft(recipeId) {
            overlayCraft.classList.remove('active');
            doAction('craft', { item_id: recipeId });
        },
        useItem(itemId) {
            closeAllOverlays();
            doAction('use_item', { item_id: itemId });
        },
        move(locationId) {
            closeAllOverlays();
            doAction('move', { target: locationId });
        },
        attack() { doAction('attack'); },
        defend() { doAction('defend'); },
        flee() { doAction('flee'); },
        loadSave,
        saveGame,
        showSaves,
    };
})();
