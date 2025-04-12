// Get the table ID from the Flask template (this will be passed from Flask)
const tableId = document.body.dataset.tableId;
console.log("Picked tableId:", tableId);

const startDateInput = document.getElementById("startDate");
const endDateInput = document.getElementById("endDate");

const table = document.getElementById(tableId);
const rows = table.getElementsByTagName("tr");

// Function to filter table rows based on the date range
function filterTable() {
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);

    for (let i = 1; i < rows.length; i++) {
        const dateCell = rows[i].getElementsByTagName("td")[0];
        if (dateCell) {
            const rowDate = new Date(dateCell.textContent.trim());

            if ((!isNaN(startDate) && rowDate < startDate) || (!isNaN(endDate) && rowDate > endDate)) {
                rows[i].style.display = "none";
            } else {
                rows[i].style.display = "";
            }
        }
    }

    updateFilteredTotal(tableId);
}

startDateInput.addEventListener("change", filterTable);
endDateInput.addEventListener("change", filterTable);

 // Clear date filter
 document.getElementById("clearDateFilter").addEventListener("click", function () {
    startDateInput.value = "";
    endDateInput.value = "";

    for (let i = 1; i < rows.length; i++) {
        rows[i].style.display = "";
    }

    updateFilteredTotal(tableId);
});

function updateFilteredTotal(tableId) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll("tbody tr");
    let total = 0;

    rows.forEach(row => {
        if (row.style.display !== "none") {
            const amountCell = row.cells[5];
            const text = amountCell.innerText.replace(/[,/=]/g, "");
            const amount = parseFloat(text);
            if (!isNaN(amount)) {
                total += amount;
            }
        }
    });

    const formatted = new Intl.NumberFormat().format(total) + "/=";
    document.getElementById("filteredTotal").innerText = formatted;
}