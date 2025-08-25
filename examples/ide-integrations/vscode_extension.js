/**
 * VSCode Extension for AutoGen Engine Integration
 * 
 * This extension provides a VSCode interface to control and monitor
 * the AutoGen Multi-Agent Development Engine.
 */

const vscode = require('vscode');
const WebSocket = require('ws');

class AutoGenEngineClient {
    constructor(host = 'localhost', port = 8765) {
        this.host = host;
        this.port = port;
        this.ws = null;
        this.connected = false;
        this.statusBarItem = null;
        this.outputChannel = null;
    }

    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(`ws://${this.host}:${this.port}`);
                
                this.ws.on('open', () => {
                    this.connected = true;
                    this.updateStatusBar('🟢 AutoGen Connected');
                    this.log('Connected to AutoGen engine');
                    resolve(true);
                });
                
                this.ws.on('message', (data) => {
                    this.handleMessage(JSON.parse(data));
                });
                
                this.ws.on('close', () => {
                    this.connected = false;
                    this.updateStatusBar('🔴 AutoGen Disconnected');
                    this.log('Disconnected from AutoGen engine');
                });
                
                this.ws.on('error', (error) => {
                    this.connected = false;
                    this.updateStatusBar('🔴 AutoGen Error');
                    this.log(`WebSocket error: ${error.message}`);
                    reject(error);
                });
                
            } catch (error) {
                reject(error);
            }
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    async sendCommand(command, params = {}) {
        if (!this.connected) {
            throw new Error('Not connected to AutoGen engine');
        }

        return new Promise((resolve, reject) => {
            const message = {
                command: command,
                params: params,
                timestamp: Date.now() / 1000,
                request_id: `req_${Date.now()}`
            };

            this.ws.send(JSON.stringify(message), (error) => {
                if (error) {
                    reject(error);
                }
            });

            // Set up response handler
            const responseHandler = (data) => {
                const response = JSON.parse(data);
                if (response.request_id === message.request_id) {
                    this.ws.removeListener('message', responseHandler);
                    resolve(response);
                }
            };

            this.ws.on('message', responseHandler);
        });
    }

    handleMessage(message) {
        if (message.type === 'status_update') {
            this.updateStatusDisplay(message.data);
        }
    }

    updateStatusDisplay(status) {
        // Update status bar with current sprint info
        if (status.current_sprint) {
            const progress = Math.round(status.progress * 100);
            this.updateStatusBar(`🔄 Sprint ${status.sprint_number}: ${progress}% - ${status.current_agent}`);
        }
    }

    updateStatusBar(text) {
        if (this.statusBarItem) {
            this.statusBarItem.text = text;
        }
    }

    log(message) {
        if (this.outputChannel) {
            this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
        }
    }

    async startProject(projectType, workDir, projectGoal) {
        try {
            const response = await this.sendCommand('start_project', {
                project_type: projectType,
                work_dir: workDir,
                project_goal: projectGoal
            });

            if (response.success) {
                this.log(`Project started: ${projectGoal}`);
                return true;
            } else {
                this.log(`Failed to start project: ${response.message}`);
                return false;
            }
        } catch (error) {
            this.log(`Error starting project: ${error.message}`);
            return false;
        }
    }

    async runSprint(sprintNumber = 1) {
        try {
            const response = await this.sendCommand('run_sprint', {
                sprint_number: sprintNumber
            });

            if (response.success) {
                this.log(`Sprint ${sprintNumber} started`);
                return true;
            } else {
                this.log(`Failed to start sprint: ${response.message}`);
                return false;
            }
        } catch (error) {
            this.log(`Error running sprint: ${error.message}`);
            return false;
        }
    }

    async getStatus() {
        try {
            const response = await this.sendCommand('get_status');
            return response.success ? response.data : null;
        } catch (error) {
            this.log(`Error getting status: ${error.message}`);
            return null;
        }
    }

    async getSprintResults(sprintNumber = null) {
        try {
            const params = {};
            if (sprintNumber !== null) {
                params.sprint_number = sprintNumber;
            }

            const response = await this.sendCommand('get_sprint_results', params);
            return response.success ? response.data.results : null;
        } catch (error) {
            this.log(`Error getting sprint results: ${error.message}`);
            return null;
        }
    }
}

class AutoGenExtension {
    constructor() {
        this.client = new AutoGenEngineClient();
        this.statusBarItem = null;
        this.outputChannel = null;
    }

    activate(context) {
        this.outputChannel = vscode.window.createOutputChannel('AutoGen Engine');
        this.client.outputChannel = this.outputChannel;

        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.text = '🔴 AutoGen Disconnected';
        this.statusBarItem.tooltip = 'AutoGen Engine Status';
        this.statusBarItem.show();
        this.client.statusBarItem = this.statusBarItem;

        // Register commands
        let connectCommand = vscode.commands.registerCommand('autogen.connect', () => {
            this.connect();
        });

        let disconnectCommand = vscode.commands.registerCommand('autogen.disconnect', () => {
            this.disconnect();
        });

        let startProjectCommand = vscode.commands.registerCommand('autogen.startProject', () => {
            this.startProject();
        });

        let runSprintCommand = vscode.commands.registerCommand('autogen.runSprint', () => {
            this.runSprint();
        });

        let showStatusCommand = vscode.commands.registerCommand('autogen.showStatus', () => {
            this.showStatus();
        });

        let showResultsCommand = vscode.commands.registerCommand('autogen.showResults', () => {
            this.showResults();
        });

        context.subscriptions.push(
            connectCommand,
            disconnectCommand,
            startProjectCommand,
            runSprintCommand,
            showStatusCommand,
            showResultsCommand,
            this.statusBarItem,
            this.outputChannel
        );

        this.log('AutoGen Engine extension activated');
    }

    deactivate() {
        this.disconnect();
    }

    async connect() {
        try {
            await this.client.connect();
            vscode.window.showInformationMessage('Connected to AutoGen engine');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to connect: ${error.message}`);
        }
    }

    disconnect() {
        this.client.disconnect();
        vscode.window.showInformationMessage('Disconnected from AutoGen engine');
    }

    async startProject() {
        if (!this.client.connected) {
            vscode.window.showErrorMessage('Not connected to AutoGen engine');
            return;
        }

        // Get project details from user
        const projectType = await vscode.window.showQuickPick([
            'typescript', 'python', 'react', 'nodejs', 'java', 'go', 'rust', 'custom'
        ], {
            placeHolder: 'Select project type'
        });

        if (!projectType) return;

        const workDir = await vscode.window.showInputBox({
            prompt: 'Enter work directory',
            value: './my-project'
        });

        if (!workDir) return;

        const projectGoal = await vscode.window.showInputBox({
            prompt: 'Enter project goal',
            value: 'Build a new project'
        });

        if (!projectGoal) return;

        // Start project
        const success = await this.client.startProject(projectType, workDir, projectGoal);
        
        if (success) {
            vscode.window.showInformationMessage('Project started successfully');
        } else {
            vscode.window.showErrorMessage('Failed to start project');
        }
    }

    async runSprint() {
        if (!this.client.connected) {
            vscode.window.showErrorMessage('Not connected to AutoGen engine');
            return;
        }

        const sprintNumber = await vscode.window.showInputBox({
            prompt: 'Enter sprint number',
            value: '1'
        });

        if (!sprintNumber) return;

        const success = await this.client.runSprint(parseInt(sprintNumber));
        
        if (success) {
            vscode.window.showInformationMessage(`Sprint ${sprintNumber} started`);
        } else {
            vscode.window.showErrorMessage('Failed to start sprint');
        }
    }

    async showStatus() {
        if (!this.client.connected) {
            vscode.window.showErrorMessage('Not connected to AutoGen engine');
            return;
        }

        const status = await this.client.getStatus();
        if (status) {
            const statusText = `
Project: ${status.project_goal}
Type: ${status.project_type}
Work Directory: ${status.work_dir}
Engine Running: ${status.is_running ? 'Yes' : 'No'}
Completed Sprints: ${status.completed_sprints}/${status.total_sprints}
            `.trim();

            vscode.window.showInformationMessage(statusText);
        } else {
            vscode.window.showErrorMessage('Failed to get status');
        }
    }

    async showResults() {
        if (!this.client.connected) {
            vscode.window.showErrorMessage('Not connected to AutoGen engine');
            return;
        }

        const results = await this.client.getSprintResults();
        if (results && results.length > 0) {
            const resultsText = results.map(result => 
                `Sprint ${result.sprint_number}: ${result.success ? '✅' : '❌'} (${result.iterations_completed} iterations)`
            ).join('\n');

            vscode.window.showInformationMessage(resultsText);
        } else {
            vscode.window.showInformationMessage('No sprint results available');
        }
    }

    log(message) {
        this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
    }
}

module.exports = {
    AutoGenExtension
};
