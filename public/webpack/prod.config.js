const path = require('path');

const SentryWebpackPlugin = require('@sentry/webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin'); // clean build dir before building
const TerserPlugin = require('terser-webpack-plugin');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');

const APP_VERSION = process.env.APP_VERSION || 'v1';
const LOCAL_BUILD = process.env.LOCAL_BUILD === '1';
const DEBUG = process.env.DEBUG === '1';
const BUILD_DIR = LOCAL_BUILD ? 'local' : 'prod';

let __outputdir = path.join(
  __dirname,
  `../assets/${APP_VERSION}/dist/${BUILD_DIR}`
);

// TODO: add css minimization
const config = {
  mode: 'production',

  devtool: LOCAL_BUILD ? 'source-map' : 'hidden-source-map',

  output: {
    path: __outputdir,
    filename: '[name]-[contenthash].js',
    chunkFilename: '[name].[contenthash].js',
    publicPath: `/static/${APP_VERSION}/dist/${BUILD_DIR}/`,
    assetModuleFilename: ({ filename }) => {
      // Keeps file structure to the asset file
      const absPathToFile = path.resolve(filename);
      const nodeModulesDir = path.join(
        path.dirname(absPathToFile).split('node_modules')[0],
        'node_modules'
      );
      // relative to the module
      const filepath = path.dirname(
        path.relative(nodeModulesDir, absPathToFile)
      );
      return `assets/${filepath}/[hash][ext][query]`;
    }
  },

  stats: {
    colors: false,
    errorDetails: true,
    hash: true,
    timings: true,
    assets: true,
    chunks: true,
    chunkModules: true,
    modules: true,
    children: true
  },

  optimization: {
    runtimeChunk: 'single',
    moduleIds: 'deterministic',
    concatenateModules: true,
    minimize: !DEBUG,
    minimizer: [
      new TerserPlugin({
        extractComments: true, // extract licenses into separate file
        // TODO: consider to use https://webpack.js.org/plugins/terser-webpack-plugin/#swc (TODO: remove console.debug with swc)
        terserOptions: {
          compress: {
            pure_funcs: ['console.debug']
          }
        }
      })
    ]
  },

  plugins: [
    new CleanWebpackPlugin({
      verbose: true,
      cleanOnceBeforeBuildPatterns: ['**/*', '!.gitattributes']
    }),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    // Ignore all locale files of moment.js
    new webpack.IgnorePlugin({
      resourceRegExp: /^\.\/locale$/,
      contextRegExp: /moment$/
    }),
    new BundleTracker({
      path: __outputdir,
      filename: path.join(__outputdir, `./webpack-stats-${APP_VERSION}.json`),
      relativePath: true
    })
  ]
};

if (!LOCAL_BUILD) {
  const sentryPlugins = [
    new SentryWebpackPlugin({
      include: [__outputdir],
      ignoreFile: '.sentrycliignore',
      ignore: ['node_modules'],
      urlPrefix: `~/static/${APP_VERSION}/dist/js`,
      debug: true,
      dryRun: LOCAL_BUILD,
      // Fail silently in case no auth data provided to the sentry-cli
      errorHandler: function (err, invokeErr) {
        console.log(`Sentry CLI Plugin: ${err.message}`);
      }
    })
    // TODO: Delete source maps after uploading to sentry.io
  ];
  config.plugins.push(...sentryPlugins);
}

module.exports = config;
