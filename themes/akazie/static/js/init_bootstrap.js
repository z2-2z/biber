/*
This file contains some functions to initialize
bootstrap elements such as popovers, tooltips and modals.
*/

function enable_popovers() {
    let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function enable_tooltips() {
    let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function enable_modals() {
    let modals = [].slice.call(document.querySelectorAll('div.modal'));
    let modalList = modals.map(function (el) {
        let m = new bootstrap.Modal(el);
        m.show();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    enable_popovers();
    enable_tooltips();
    enable_modals();
});
