const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const webpack = require('webpack');
const fs = require('fs');
const os = require('os');

module.exports = (env, argv) => {
  const isDev = argv.mode === 'development';

  // Use Office dev certs
  const certPath = path.join(os.homedir(), '.office-addin-dev-certs');
  const httpsOptions = fs.existsSync(certPath) ? {
    key: fs.readFileSync(path.join(certPath, 'localhost.key')),
    cert: fs.readFileSync(path.join(certPath, 'localhost.crt'))
  } : true;

  return {
    entry: {
      taskpane: './taskpane/index.tsx',
      commands: './commands/commands.ts'
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: '[name].js',
      clean: true
    },
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx']
    },
    module: {
      rules: [
        {
          test: /\.(ts|tsx)$/,
          use: 'babel-loader',
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: 'asset/resource'
        }
      ]
    },
    plugins: [
      new webpack.DefinePlugin({
        'process.env.REACT_APP_API_URL': JSON.stringify(process.env.REACT_APP_API_URL || 'https://localhost:3001')
      }),
      new HtmlWebpackPlugin({
        template: './taskpane/taskpane.html',
        filename: 'taskpane.html',
        chunks: ['taskpane']
      }),
      new HtmlWebpackPlugin({
        template: './commands/commands.html',
        filename: 'commands.html',
        chunks: ['commands']
      }),
      new CopyWebpackPlugin({
        patterns: [
          { from: '../assets', to: 'assets', noErrorOnMissing: true }
        ]
      })
    ],
    devServer: {
      static: {
        directory: path.join(__dirname, 'dist')
      },
      port: 3000,
      hot: true,
      server: {
        type: 'https',
        options: httpsOptions
      },
      headers: {
        'Access-Control-Allow-Origin': '*'
      },
      proxy: {
        '/api': {
          target: 'http://localhost:3001',
          secure: false,
          changeOrigin: true
        },
        '/health': {
          target: 'http://localhost:3001',
          secure: false,
          changeOrigin: true
        }
      }
    },
    devtool: isDev ? 'source-map' : false
  };
};
