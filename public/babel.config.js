module.exports = api => {
  const isEnvTest = api.env('test');
  return {
    presets: [
      [
        'module:@cscenter/babel-preset',
        {
          presetUseBuiltIns: 'usage',
          typescript: false,
          runtime: 'classic'
        }
      ]
    ],
    plugins: [
      isEnvTest && ['@babel/plugin-transform-modules-commonjs'],
      isEnvTest && ['dynamic-import-node'],
      // Stage 2
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      '@babel/plugin-proposal-function-sent',
      '@babel/plugin-proposal-throw-expressions',
      // Stage 3
      '@babel/plugin-syntax-dynamic-import',
      '@babel/plugin-syntax-import-meta'
    ].filter(Boolean)
  };
};
