document.querySelectorAll('.clickable').forEach(img => {
    img.addEventListener('click', function() {
        document.querySelectorAll('.clickable').forEach(otherImg => {
            if (otherImg !== this) {
                otherImg.classList.remove('zoomed');
            }
        });
        this.classList.toggle('zoomed');
    });
});
