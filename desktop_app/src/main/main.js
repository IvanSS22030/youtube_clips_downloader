import { app, BrowserWindow } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// ESM Replacements for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow;
let pythonProcess;

const API_PORT = 8000;
const PY_DIST_FOLDER = 'backend'; // For prod
const PY_FOLDER = 'backend';      // For dev
const PY_MODULE = 'main';         // main.py

// Determine Python Path
// In Dev: ../../backend/venv/Scripts/python.exe
// In Prod: ./backend/main.exe (if compiled) or bundled python
const isDev = !app.isPackaged;
const pythonExecutable = isDev
    ? path.join(__dirname, '../../backend/venv/Scripts/python.exe')
    : path.join(process.resourcesPath, 'backend/venv/Scripts/python.exe'); // Adjust for prod later

const pythonScript = isDev
    ? path.join(__dirname, '../../backend/main.py')
    : path.join(process.resourcesPath, 'backend/main.py');


function startPythonBackend() {
    console.log('Starting Python Backend...');
    console.log('Python Path:', pythonExecutable);
    console.log('Script Path:', pythonScript);

    if (isDev) {
        // In dev, run python main.py via uvicorn programmatically or just python main.py
        // Since main.py has `if __name__ == "__main__": uvicorn.run(...)`, we can just run python main.py
        pythonProcess = spawn(pythonExecutable, [pythonScript], {
            cwd: path.join(__dirname, '../../backend'), // Set CWD to backend so imports work
        });
    } else {
        // Prod logic later
        pythonProcess = spawn(pythonExecutable, [pythonScript]);
    }

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python]: ${data} `);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Err]: ${data} `);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code} `);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        backgroundColor: '#1a1a1a', // Dark mode bg
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // For easier IPC in this PoC
        },
    });

    if (isDev) {
        // Wait for Vite to be ready
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'));
    }

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

app.on('ready', () => {
    startPythonBackend();

    // Wait for API to be ready before showing window? 
    // Or just show window and let it retry connection. 
    // Let's just create window immediately, React handles connection state.
    createWindow();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});
