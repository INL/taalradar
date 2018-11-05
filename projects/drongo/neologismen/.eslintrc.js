module.exports = {
    "env": {
        "browser": true,
        "jquery": true
    },
    "plugins": ["html","compat"],
    "parserOptions": {
        "ecmaVersion": 5
    },
    "rules": {
        "no-console": "off",
        "indent": [
            "warn",
            "tab"
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "quotes": [
            "error",
            "double"
        ],
        "semi": [
            "error",
            "always"
        ],
        "compat/compat": "error"
    }
};