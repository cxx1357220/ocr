const fs = require('fs')
fs.cp('./html_dist', './dist/ocr/_internal', {
    recursive: true
}, (err) => {
    if (err) {
        console.error(err);
    }
});