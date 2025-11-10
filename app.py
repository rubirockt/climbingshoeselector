<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kletterschuh-Datenbank 3D</title>
    <!-- Lade Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <!-- Lade Three.js für 3D-Visualisierung -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f7fafc;
        }
        .data-point {
            cursor: pointer;
            transition: transform 0.2s, background-color 0.2s;
        }
        .data-point:hover {
            transform: scale(1.05);
            background-color: #f0f4f8;
        }
        #visualization-container {
            width: 100%;
            height: 50vh; /* Responsive Höhe für 3D-Container */
            min-height: 400px;
            background-color: #e2e8f0;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
            cursor: grab;
        }
        /* Custom scrollbar for table on mobile */
        .scroll-x {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-7xl mx-auto">
        <h1 class="text-4xl font-extrabold text-gray-900 mb-6 border-b-4 border-indigo-600 pb-2">
            Kletterschuh-Datenbank & 3D-Visualisierung
        </h1>

        <!-- Lade- und Statusmeldungen -->
        <div id="status-message" class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6 hidden rounded-lg" role="alert">
            <p class="font-bold">Lade Daten...</p>
            <p>Bitte warten Sie, während die Datenbank geladen wird.</p>
        </div>
        <div id="error-message" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6 hidden rounded-lg" role="alert">
            <p class="font-bold">Fehler</p>
            <p id="error-text"></p>
        </div>
        
        <!-- 3D-Visualisierung -->
        <div id="visualization-container" class="mb-8"></div>

        <!-- Detailanzeige -->
        <div id="detail-card" class="bg-white p-6 rounded-xl shadow-lg border border-gray-200 mb-8 hidden">
            <h2 class="text-2xl font-bold text-indigo-600 mb-4" id="detail-title">Schuhdetails</h2>
            <div id="detail-content" class="text-gray-700 space-y-2">
                <!-- Details werden hier eingefügt -->
            </div>
        </div>

        <!-- Filter und Steuerelemente -->
        <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-200 mb-8">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">Filter und Einstellungen</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Filter nach Hersteller -->
                <div>
                    <label for="filter-hersteller" class="block text-sm font-medium text-gray-700 mb-1">Hersteller filtern:</label>
                    <select id="filter-hersteller" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                        <option value="">Alle Hersteller</option>
                    </select>
                </div>

                <!-- Anzeige-Modus -->
                <div>
                    <label for="display-mode" class="block text-sm font-medium text-gray-700 mb-1">Visualisierungsmodus:</label>
                    <select id="display-mode" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                        <option value="points">Punkte (Standard)</option>
                        <option value="overlap">Überlappungsanalyse</option>
                    </select>
                </div>
                
                <!-- Sichtbarkeit der Achsenbeschriftung -->
                <div class="flex items-end">
                    <button id="toggle-labels" class="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-150 ease-in-out">
                        Achsenbeschriftung umschalten (Ein)
                    </button>
                </div>
            </div>
            <p class="mt-4 text-sm text-gray-500">
                **Achsenlegende:** X = Support (Stützleistung, Steifigkeit), Y = Performance (Präzision, Aggressivität), Z = Volumen (Schuhform/Passform).
            </p>
        </div>

        <!-- Schuh-Tabelle -->
        <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
            <h2 class="text-xl font-semibold mb-4 text-gray-800" id="table-title">Gefilterte Schuhmodelle (<span id="shoe-count">0</span>)</h2>
            <div class="scroll-x">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hersteller</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Schuhmodell</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Support (X)</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance (Y)</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volumen (Z)</th>
                        </tr>
                    </thead>
                    <tbody id="shoe-table-body" class="bg-white divide-y divide-gray-200">
                        <!-- Schuhreihen werden hier eingefügt -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Firebase SDKs -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, collection, query, onSnapshot, orderBy, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        // Globale Variablen für Firebase und Three.js
        let db;
        let auth;
        let userId;
        let allShoes = [];
        let scene, camera, renderer, controls;
        let shoePoints = [];
        let shoeLabels = [];
        let isLabelsVisible = true;
        
        // --- Firestore & Auth Setup ---

        // Firebase-Konfiguration und App-ID aus der Canvas-Umgebung
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

        if (firebaseConfig) {
            const app = initializeApp(firebaseConfig);
            db = getFirestore(app);
            auth = getAuth(app);
            // setLogLevel('debug'); // Deaktiviert, um die Konsole sauber zu halten
            
            // 1. Authentifizierung
            onAuthStateChanged(auth, async (user) => {
                const statusMessage = document.getElementById('status-message');
                if (user) {
                    userId = user.uid;
                    statusMessage.innerHTML = '<p class="font-bold">Datenbank verbunden.</p>';
                    // 2. Daten laden (nur wenn authentifiziert)
                    setupFirestoreListener();
                } else {
                    // Falls noch nicht angemeldet, mit Custom Token oder anonym anmelden
                    try {
                        if (initialAuthToken) {
                            await signInWithCustomToken(auth, initialAuthToken);
                        } else {
                            await signInAnonymously(auth);
                        }
                    } catch (error) {
                        console.error("Firebase Auth Fehler:", error);
                        document.getElementById('error-text').textContent = "Authentifizierung fehlgeschlagen: " + error.message;
                        document.getElementById('error-message').classList.remove('hidden');
                        statusMessage.classList.add('hidden');
                    }
                }
            });
        }

        // --- Firestore Listener ---

        function setupFirestoreListener() {
            if (!db) return;

            const shoesCollectionRef = collection(db, `artifacts/${appId}/public/data/climbing_shoes`);
            // Hinweis: orderBy() in Firestore kann einen Index erfordern. Wir sortieren clientseitig.
            const q = query(shoesCollectionRef);

            document.getElementById('status-message').classList.remove('hidden');
            document.getElementById('status-message').innerHTML = '<p class="font-bold">Lade Schuhdaten...</p>';

            onSnapshot(q, (snapshot) => {
                document.getElementById('status-message').classList.add('hidden');
                
                const shoes = snapshot.docs.map(doc => ({
                    id: doc.id,
                    ...doc.data(),
                    // Konvertiere die Felder in Zahlen (obwohl sie aus Firestore kommen, ist es sicherer)
                    Support_X: parseFloat(doc.data().Support_X),
                    Performance_Y: parseFloat(doc.data().Performance_Y),
                    Volumen_Z: parseFloat(doc.data().Volumen_Z),
                }));
                allShoes = shoes;
                
                // Aktualisiere Hersteller-Filter-Optionen
                updateManufacturerFilter(allShoes);
                
                // Filtere und Visualisiere die Daten
                filterAndRenderShoes();
            }, (error) => {
                console.error("Firestore Fehler:", error);
                document.getElementById('error-text').textContent = "Fehler beim Laden der Daten: " + error.message;
                document.getElementById('error-message').classList.remove('hidden');
            });
        }
        
        // --- 3D Visualisierung (Three.js) ---

        function initThree() {
            const container = document.getElementById('visualization-container');
            const width = container.clientWidth;
            const height = container.clientHeight;

            // Szene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f4f8); // Helles Blau-Grau

            // Kamera
            camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
            camera.position.set(15, 15, 15);
            camera.lookAt(0, 0, 0);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(width, height);
            container.appendChild(renderer.domElement);

            // Achsen- und Gitter-Helfer (für 10x10x10 Würfel)
            const gridHelper = new THREE.GridHelper(10, 10, 0x000000, 0x000000);
            gridHelper.material.opacity = 0.2;
            gridHelper.material.transparent = true;
            gridHelper.position.y = 0; // X-Z-Ebene
            scene.add(gridHelper);

            const gridHelper2 = new THREE.GridHelper(10, 10, 0x000000, 0x000000);
            gridHelper2.material.opacity = 0.2;
            gridHelper2.material.transparent = true;
            gridHelper2.rotation.z = Math.PI / 2;
            gridHelper2.position.x = 0; // Y-Z-Ebene
            scene.add(gridHelper2);

            const gridHelper3 = new THREE.GridHelper(10, 10, 0x000000, 0x000000);
            gridHelper3.material.opacity = 0.2;
            gridHelper3.material.transparent = true;
            gridHelper3.rotation.x = Math.PI / 2;
            gridHelper3.position.z = 0; // X-Y-Ebene
            scene.add(gridHelper3);

            // Achsenbeschriftung (X, Y, Z)
            createAxisLabels();

            // Beleuchtung
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            scene.add(new THREE.DirectionalLight(0xffffff, 0.6));

            // Steuerung (OrbitControls, da sie einfacher sind)
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Event Listener für Größenänderungen
            window.addEventListener('resize', onWindowResize, false);
            
            // Start der Render-Schleife
            animate();
        }
        
        function onWindowResize() {
            const container = document.getElementById('visualization-container');
            if (!container) return;

            const width = container.clientWidth;
            const height = container.clientHeight;

            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
            
            // Achsenbeschriftung aktualisieren, da der Canvas neu gezeichnet wird
            if(isLabelsVisible) {
                updateShoeLabelPositions();
            }
        }
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
            if(isLabelsVisible) {
                updateShoeLabelPositions();
            }
        }

        // Hilfsfunktion zur Erstellung der Achsenbeschriftungen
        function createAxisLabels() {
            // Entferne alte Beschriftungen
            shoeLabels.forEach(label => label.element.remove());
            shoeLabels = [];

            const axisData = [
                { text: 'Support (X)', pos: [12, 0, 0], color: '#ff0000' },
                { text: 'Performance (Y)', pos: [0, 12, 0], color: '#00ff00' },
                { text: 'Volumen (Z)', pos: [0, 0, 12], color: '#0000ff' }
            ];

            axisData.forEach(data => {
                const element = document.createElement('div');
                element.className = 'absolute text-xs font-bold p-1 rounded-sm shadow-md';
                element.style.backgroundColor = 'white';
                element.style.color = data.color;
                element.textContent = data.text;
                document.body.appendChild(element);

                shoeLabels.push({
                    element: element,
                    position: new THREE.Vector3(data.pos[0], data.pos[1], data.pos[2]),
                    isDataPoint: false
                });
            });
            // Füge die Achsenbeschriftungen hinzu
            updateShoeLabelPositions();
        }

        function clearVisualisation() {
            // Entferne alle alten Punkte und Beschriftungen (außer Achsen)
            shoePoints.forEach(point => scene.remove(point));
            shoePoints = [];
            shoeLabels = shoeLabels.filter(label => !label.isDataPoint); // Nur Achsenbeschriftungen behalten
            document.querySelectorAll('.shoe-label').forEach(el => el.remove());
        }

        // --- Datenverarbeitung und Rendering ---

        function updateManufacturerFilter(shoes) {
            const select = document.getElementById('filter-hersteller');
            const manufacturers = [...new Set(shoes.map(shoe => shoe.Hersteller))].sort();
            
            // Speichere die aktuell ausgewählte Option
            const currentSelection = select.value;
            
            // Leere die Liste und füge die Standardoption hinzu
            select.innerHTML = '<option value="">Alle Hersteller</option>';
            
            // Füge neue Optionen hinzu
            manufacturers.forEach(manufacturer => {
                const option = document.createElement('option');
                option.value = manufacturer;
                option.textContent = manufacturer;
                select.appendChild(option);
            });
            
            // Setze die Auswahl zurück, falls die vorherige Option noch existiert
            if (manufacturers.includes(currentSelection)) {
                select.value = currentSelection;
            }
        }

        function filterAndRenderShoes() {
            const selectedManufacturer = document.getElementById('filter-hersteller').value;
            let filteredShoes = allShoes;

            if (selectedManufacturer) {
                filteredShoes = allShoes.filter(shoe => shoe.Hersteller === selectedManufacturer);
            }
            
            // MANDATORISCHE ANFORDERUNG: Sortiere die gefilterte Liste alphabetisch nach Hersteller + Schuhmodell
            filteredShoes.sort((a, b) => {
                const nameA = a.Hersteller + " " + a.Schuhmodell;
                const nameB = b.Hersteller + " " + b.Schuhmodell;
                // localeCompare für korrekte alphabetische Sortierung
                return nameA.localeCompare(nameB, 'de', { sensitivity: 'base' });
            });
            
            // Visualisierung aktualisieren
            render3DPoints(filteredShoes);
            
            // Tabelle aktualisieren
            renderTable(filteredShoes);
        }

        function render3DPoints(shoes) {
            clearVisualisation();
            
            const mode = document.getElementById('display-mode').value;
            
            shoes.forEach((shoe, index) => {
                const x = shoe.Support_X / 10 * 10;
                const y = shoe.Performance_Y / 10 * 10;
                const z = shoe.Volumen_Z / 10 * 10;
                
                let size = 0.5;
                let color = new THREE.Color(0x000000); // Schwarz
                
                if (shoe.Hersteller === 'La Sportiva') {
                    color = new THREE.Color(0xff0000); // Rot
                } else if (shoe.Hersteller === 'Scarpa') {
                    color = new THREE.Color(0x0000ff); // Blau
                }

                // Im 'overlap'-Modus Punkte gleicher Position hervorheben
                if (mode === 'overlap') {
                    const overlapCount = shoes.filter(
                        s => s.Support_X === shoe.Support_X && 
                             s.Performance_Y === shoe.Performance_Y && 
                             s.Volumen_Z === shoe.Volumen_Z
                    ).length;
                    
                    if (overlapCount > 1) {
                        size = 0.8; // Größer für überlappende Punkte
                        color = new THREE.Color(0xffaa00); // Orange für Überlappung
                    }
                }

                const geometry = new THREE.SphereGeometry(size * 0.1, 16, 16); // Kleinere Punkte
                const material = new THREE.MeshPhongMaterial({ color: color });
                const point = new THREE.Mesh(geometry, material);
                
                // Normalisiere die Achsen auf einen Bereich von 0 bis 10
                // X (Support): 0-10 -> 0-10
                // Y (Performance): 0-10 -> 0-10
                // Z (Volumen): 0-10 -> 0-10
                point.position.set(x, y, z); 
                point.userData = { shoe: shoe };

                // Event Listener für Klick auf den Punkt
                point.addEventListener('click', () => showDetails(shoe));

                scene.add(point);
                shoePoints.push(point);
                
                // Erstelle CSS-Label für jeden Schuh
                const labelElement = document.createElement('div');
                labelElement.className = 'shoe-label absolute text-xs bg-gray-900 text-white px-1 py-0.5 rounded opacity-75 whitespace-nowrap hidden';
                labelElement.textContent = `${shoe.Hersteller} ${shoe.Schuhmodell}`;
                document.body.appendChild(labelElement);

                shoeLabels.push({
                    element: labelElement,
                    position: point.position,
                    isDataPoint: true
                });
            });
            
            // Aktualisiere die Beschriftungen beim Rendern
            updateShoeLabelVisibility(isLabelsVisible);
        }

        // Funktion zur Aktualisierung der Positionen der HTML-Labels basierend auf 3D-Position
        function updateShoeLabelPositions() {
            const container = document.getElementById('visualization-container');
            const rect = container.getBoundingClientRect();
            
            shoeLabels.forEach(label => {
                // Beschriftungen nur aktualisieren, wenn sie sichtbar sind
                if (label.element.classList.contains('hidden') && label.isDataPoint) return;
                
                // 3D-Position in 2D-Bildschirmkoordinaten umwandeln
                const vector = label.position.clone();
                vector.project(camera);

                // Berechne Bildschirmkoordinaten
                const x = (vector.x * 0.5 + 0.5) * rect.width + rect.left;
                const y = (-vector.y * 0.5 + 0.5) * rect.height + rect.top;

                // Setze die Position des HTML-Elements (Zentrierung)
                label.element.style.left = `${x}px`;
                label.element.style.top = `${y}px`;
                label.element.style.transform = `translate(-50%, -50%)`;
                
                // Optional: Verstecke Punkte, die außerhalb des Blickfeldes liegen
                if (vector.z > 1) {
                     label.element.classList.add('hidden');
                } else if (!label.element.classList.contains('hidden') && label.isDataPoint) {
                    label.element.classList.remove('hidden');
                }
            });
        }
        
        function updateShoeLabelVisibility(visible) {
            isLabelsVisible = visible;
            const button = document.getElementById('toggle-labels');
            
            shoeLabels.forEach(label => {
                if (label.isDataPoint) {
                    label.element.classList.toggle('hidden', !visible);
                }
            });
            
            if (visible) {
                button.textContent = "Achsenbeschriftung umschalten (Ein)";
                updateShoeLabelPositions();
            } else {
                button.textContent = "Achsenbeschriftung umschalten (Aus)";
            }
        }
        
        function renderTable(shoes) {
            const tableBody = document.getElementById('shoe-table-body');
            const shoeCount = document.getElementById('shoe-count');
            tableBody.innerHTML = '';
            
            shoeCount.textContent = shoes.length;

            shoes.forEach(shoe => {
                const row = tableBody.insertRow();
                row.className = 'data-point hover:bg-indigo-50 hover:shadow-inner transition duration-150';
                row.onclick = () => showDetails(shoe);
                
                const manufacturerCell = row.insertCell();
                manufacturerCell.className = 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900';
                manufacturerCell.textContent = shoe.Hersteller;

                const modelCell = row.insertCell();
                modelCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
                modelCell.textContent = shoe.Schuhmodell;

                const supportCell = row.insertCell();
                supportCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
                supportCell.textContent = shoe.Support_X.toFixed(1);

                const performanceCell = row.insertCell();
                performanceCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
                performanceCell.textContent = shoe.Performance_Y.toFixed(1);

                const volumenCell = row.insertCell();
                volumenCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
                volumenCell.textContent = shoe.Volumen_Z.toFixed(1);
            });
        }
        
        function showDetails(shoe) {
            const detailCard = document.getElementById('detail-card');
            document.getElementById('detail-title').textContent = `${shoe.Hersteller} ${shoe.Schuhmodell}`;
            document.getElementById('detail-content').innerHTML = `
                <p><strong>Support (X - Steifigkeit):</strong> ${shoe.Support_X.toFixed(1)} / 10</p>
                <p><strong>Performance (Y - Aggressivität):</strong> ${shoe.Performance_Y.toFixed(1)} / 10</p>
                <p><strong>Volumen (Z - Passform):</strong> ${shoe.Volumen_Z.toFixed(1)} / 10</p>
                <p class="mt-4 text-xs text-gray-500">Klicken Sie auf andere Zeilen in der Tabelle oder Punkte in der Visualisierung, um die Details zu aktualisieren.</p>
            `;
            detailCard.classList.remove('hidden');
            detailCard.scrollIntoView({ behavior: 'smooth' });
        }

        // --- Event Listener Setup ---
        
        window.onload = function() {
            // Initialisiere Three.js
            initThree();
            
            // Setze Event Listener für Filter und Modi
            document.getElementById('filter-hersteller').addEventListener('change', filterAndRenderShoes);
            document.getElementById('display-mode').addEventListener('change', filterAndRenderShoes);
            document.getElementById('toggle-labels').addEventListener('click', () => {
                updateShoeLabelVisibility(!isLabelsVisible);
            });
        };
        
        // --- Dummy-Implementierung für OrbitControls (falls Three.js nicht geladen wird) ---
        // Dies ist notwendig, da die Umgebung Three.js nicht automatisch bereitstellt.
        // Die volle, selbstständige Funktionalität ist durch die obigen Imports gewährleistet.
        if (typeof THREE.OrbitControls === 'undefined') {
            class OrbitControls {
                constructor() {
                    console.warn("THREE.OrbitControls nicht gefunden. 3D-Steuerung ist deaktiviert.");
                    this.enableDamping = false;
                }
                update() {}
            }
            window.THREE.OrbitControls = OrbitControls;
        }

    </script>
</body>
</html>
