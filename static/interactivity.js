document.addEventListener("DOMContentLoaded", () => {
    // Changing background of the stock status depending on status
    const productRows = document.querySelectorAll(".product-row");
    console.log("Rows found:", productRows.length);


    productRows.forEach(row => {
        const statusCell = row.querySelector(".stock_status-column");

        if (statusCell) {
            const status = statusCell.textContent.trim().toLowerCase();
            console.log("Status:", status);

            switch (status) {
                case "all good":
                    console.log("Status is 'all good' – row will be green.");
                    row.style.backgroundColor = "rgba(23, 216, 68, 0.5)"; // Green
                    row.style.color = "black";
                    break;
                case "needs restocking":
                    row.style.backgroundColor = "rgba(253, 144, 20, 0.5)";  // Orange
                    row.style.color = "black";
                    break;
                case "overstocked":
                    row.style.backgroundColor = "#ffc107"; // Yellow
                    row.style.color = "black";
                    break;
                case "out of stock":
                    row.style.backgroundColor = "#dc3545"; // Red
                    row.style.color = "white";
                    break;
                default:
                    row.style.backgroundColor = "";
                    row.style.color = "";
                    break;
            }
        }
    });

    function filterByCategory() {
        const input = document.getElementById("categoryFilter").value.toLowerCase();
        const table = document.getElementById("productsTable");
        const rows = table.getElementsByTagName("tr");
        const noResultsMessage = document.getElementById("noResultsMessage");
        let hasResults = false;

        for (let i = 0; i < rows.length; i++) {
            const categoryCell = rows[i].getElementsByTagName("td")[3];

            if (categoryCell) {
                const categoryText = categoryCell.textContent.toLowerCase();
                if (categoryText.includes(input)) {
                    rows[i].style.display = "";
                    hasResults = true;
                } else {
                    rows[i].style.display = "none";
                }
            }
        }

        noResultsMessage.style.display = hasResults ? "none" : "block";
    }

    function clearFilter() {
        document.getElementById("categoryFilter").value = "";
        filterByCategory();
    }

    function filterProducts() {
        const searchInput = document.getElementById("productSearch").value.toLowerCase();
        const rows = document.querySelectorAll(".product-row");
        let visibleRows = 0;

        rows.forEach(row => {
            const productName = row.querySelector(".product-name").textContent.toLowerCase();
            if (productName.includes(searchInput)) {
                row.style.display = "";
                visibleRows++;
            } else {
                row.style.display = "none";
            }
        });

        document.getElementById("noResults").style.display = visibleRows === 0 ? "block" : "none";
    }

    function selectProduct() {
        const selectedProduct = document.getElementById("productDropdown").value.toLowerCase();
        const searchInput = document.getElementById("productSearch");

        searchInput.value = selectedProduct;
        filterProducts();
    }

    function clearSearch() {
        document.getElementById("productSearch").value = "";
        document.getElementById("productDropdown").selectedIndex = 0;
        filterProducts();
    }
 

    // Expose filter/search functions globally if needed
    window.filterByCategory = filterByCategory;
    window.filterProducts = filterProducts;
    window.selectProduct = selectProduct;
    window.clearSearch = clearSearch;

    // Sidebar toggle logic
    const toggleButton = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.getElementById("mainContent");
    const sidebarOverlay = document.getElementById("sidebarOverlay"); // ✅ overlay

    if (toggleButton && sidebar && mainContent) {
        toggleButton.addEventListener("click", function () {
            sidebar.classList.toggle("active");
            mainContent.classList.toggle("shifted");

            // ✅ Show or hide overlay on small screens
            if (window.innerWidth < 768) {
                sidebarOverlay.classList.toggle("show");
            }
        });

        // ✅ Hide sidebar when clicking outside (on overlay)
        sidebarOverlay.addEventListener("click", function () {
            sidebar.classList.remove("active");
            mainContent.classList.remove("shifted");
            sidebarOverlay.classList.remove("show");
            mainContent.classList.toggle('shifted');
        });
    }
});
