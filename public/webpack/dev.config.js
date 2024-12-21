const path = require('path');

const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const APP_VERSION = process.env.APP_VERSION || 'v1';

let __outputdir = path.join(__dirname, `../assets/${APP_VERSION}/dist/local`);

module.exports = {
  mode: 'development',
  devtool: 'eval-cheap-source-map',

  output: {
    filename: '[name]-[fullhash].js',
    publicPath: 'http://csc.test:8081/',
    assetModuleFilename: `assets/[name].[hash][ext][query]`
  },

  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('development')
    }),
    new BundleTracker({
      path: __outputdir,
      filename: path.join(__outputdir, `./webpack-stats-${APP_VERSION}.json`)
    })
  ],

  // This is default settings for development mode, but lets set it explicitly
  optimization: {
    moduleIds: 'named',
    concatenateModules: false,
    runtimeChunk: 'single'
  },

  devServer: {
    client: {
      overlay: {
        warnings: false,
        errors: true
      }
    },
    port: 8081,
    hot: true,
    host: '0.0.0.0',
    headers: { 'Access-Control-Allow-Origin': '*' },
    allowedHosts: ['.csc.test', '.club.ru', 'lk.shad.test']
  }
};
