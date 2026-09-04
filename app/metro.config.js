const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);

// Bundle statically required ExecuTorch .pte programs as Metro assets.
config.resolver.assetExts.push("pte");

module.exports = config;
