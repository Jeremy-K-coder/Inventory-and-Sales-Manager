document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();

            // Find the associated dropdown (assuming it's the next sibling element)
            const dropdown = this.nextElementSibling;
            const arrow = this.querySelector("i");

            if (dropdown && dropdown.classList.contains("dropdown-content")) {
                // Toggle visibility
                dropdown.style.display = (dropdown.style.display === "none" || dropdown.style.display === "") ? "flex" : "none";

                // Toggle arrow rotation
                if (arrow) {
                    arrow.classList.toggle("rotate");
                }
            }
        });
    });
});