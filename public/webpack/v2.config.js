const path = require('path');

const Dotenv = require('dotenv-webpack');
const ESLintPlugin = require('eslint-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');
const { merge } = require('webpack-merge'); // merge webpack configs

process.env.BABEL_ENV = process.env.NODE_ENV;

const APP_VERSION = 'v2';
const DEVELOPMENT = process.env.NODE_ENV === 'development';

const __srcdir = path.join(__dirname, `../src/${APP_VERSION}`);
const __nodemodulesdir = path.join(__dirname, '../node_modules');
// All dependencies will be copied to path, relative to bundles output
const STATIC_URL = path.join('/static/');

const common = {
  context: __srcdir,

  entry: {
    // TODO: rename to `shared`
    common: [
      'core-js/stable',
      'regenerator-runtime/runtime', // support async
      //'jquery',
      'ky',
      'popper.js',
      'fontfaceobserver',
      'noty'
    ],
    main: { import: path.join(__srcdir, '/js/main.js'), dependOn: 'common' }
  },

  externals: {},

  resolve: {
    extensions: ['.jsx', '.js', '.ts', '.tsx'],
    modules: [path.join(__srcdir, '/js'), __nodemodulesdir],
    symlinks: false
  },

  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        include: path.resolve(__srcdir, 'js'),
        use: [{ loader: 'babel-loader' }]
      },
      {
        test: /\.(js|jsx|ts|tsx)$/,
        include: [
          path.resolve(__nodemodulesdir, 'ky'),
          path.resolve(__nodemodulesdir, 'bootstrap'),
          path.resolve(__nodemodulesdir, 'react-async'),
          path.resolve(__nodemodulesdir, 'react-hook-form')
        ],
        use: [
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: false
            }
          }
        ]
      },
      {
        test: /\.s?[ac]ss$/,
        exclude: __nodemodulesdir,
        use: [
          DEVELOPMENT ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader', // translates CSS into CommonJS modules
          'postcss-loader',
          {
            loader: 'sass-loader', // compiles SASS to CSS
            options: {
              sassOptions: {
                outputStyle: 'expanded',
                // precision: 8,
                includePaths: [__nodemodulesdir]
              }
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: [
          DEVELOPMENT ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      {
        // Serve static in node_modules/
        test: /\.woff2?$|\.ttf$|\.eot$|\.svg$|\.png$|\.jpg$|\.swf$/,
        include: __nodemodulesdir,
        type: 'asset/resource' // TODO: don't emit, serve files from node_modules instead
      }
    ]
  },

  plugins: [
    new Dotenv({
      path: path.join(__dirname, '.env'),
      silent: true
    }),
    new MiniCssExtractPlugin({
      // Options similar to the same options in webpackOptions.output
      // both options are optional
      filename: DEVELOPMENT ? '[name].css' : '[name]-[contenthash].css',
      chunkFilename: DEVELOPMENT
        ? '[id].[name].css'
        : '[name]-[contenthash].css'
    }),
    new ESLintPlugin()
  ],

  optimization: {
    splitChunks: {
      chunks: 'all',
      minSize: 30000,
      minChunks: 2,
      maxAsyncRequests: 6,
      maxInitialRequests: 4,
      automaticNameDelimiter: '~',
      // name: true,
      cacheGroups: {
        // Add core-js modules to `common` js entrypoint
        // TODO: better to move `common` entry point imports to this chunk e.g. https://stackoverflow.com/a/48986526/1341309
        common: {
          chunks: 'all',
          test: /(common|[\\/]node_modules[\\/]core-js[\\/])/,
          name: 'common',
          enforce: true
        },
        // react: {
        //     chunks: "all",
        //     test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
        //     name: "react",
        //     enforce: true,
        // },
        vendors: {
          // chunks: "all",
          minChunks: 5,
          test: /[\\/]node_modules[\\/]/,
          priority: -10
          // name: "vendors"
          // reuseExistingChunk: true
        }
        // default: {
        //     minChunks: 2,
        //     priority: -20,
        //     reuseExistingChunk: true
        // }
      }
    }
  }
};

let appConfig;
if (DEVELOPMENT) {
  appConfig = merge(common, require('./dev.config'));
} else {
  appConfig = merge(common, require('./prod.config'));
}

module.exports = appConfig;
