
document.addEventListener("DOMContentLoaded", function(event) {
    for (c of document.head.children) {
        if (c.nodeName === "SCRIPT" && c.src.endsWith("/latex/tex-mml-chtml.js")) {
            c.id = "MathJax-script";
        }
    }
    
    MathJax = {
        tex: {
            inlineMath: []
        },
        chtml: {
            scale: 2.0,
            minScale: 1.0
        }
    };
});
