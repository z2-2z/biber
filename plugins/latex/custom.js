
document.addEventListener("DOMContentLoaded", function(event) {
    for (c of document.head.children) {
        if (c.nodeName === "SCRIPT" && c.src.endsWith("/tex-mml-chtml.js")) {
            c.id = "MathJax-script";
        }
    }
    
    MathJax = {
        tex: {
            inlineMath: []
        },
        chtml: {
            scale: 1.3
        }
    };
});
