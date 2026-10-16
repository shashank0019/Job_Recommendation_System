const react = require('@vitejs/plugin-react').default

module.exports = {
	plugins: [react()],
	server: {
		port: 5173,
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:5000',
				changeOrigin: true,
				secure: false,
			},
		},
	},
}