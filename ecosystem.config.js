module.exports = {
  apps: [{
    name: 'tender-api',
    script: '.venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 9000',
    cwd: '/root/tender-data-analyser-v2',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/root/tender-data-analyser-v2'
    }
  }]
};
