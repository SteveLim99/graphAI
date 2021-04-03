const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        '/ood',
        createProxyMiddleware({
            target: 'http://api:5000',
            changeOrigin: true,
            pathRewrite: {
                '^/ood': ''
            }
        })
    );
    app.use(
        '/gnn',
        createProxyMiddleware({
            target: 'http://gnn_api:5001',
            changeOrigin: true,
            pathRewrite: {
                '^/gnn': ''
            }
        })
    );
    app.use(
        '/db',
        createProxyMiddleware({
            target: 'http://db_api:5002',
            changeOrigin: true,
            pathRewrite: {
                '^/db': ''
            }
        })
    );
};