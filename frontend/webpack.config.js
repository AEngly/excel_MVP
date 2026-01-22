const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = (env, argv) => {
  const isDev = argv.mode === 'development';

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
      https: true,
      headers: {
        'Access-Control-Allow-Origin': '*'
      }
    },
    devtool: isDev ? 'source-map' : false
  };
};
