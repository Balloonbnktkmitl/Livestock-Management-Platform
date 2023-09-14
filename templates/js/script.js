var currentPage = 1;
var formPages = document.querySelectorAll("#register-form > div");

function nextPage() {
    if (currentPage < formPages.length) {
        formPages[currentPage - 1].classList.add("hidden");
        currentPage++;
        formPages[currentPage - 1].classList.remove("hidden");
    }
}

function prevPage() {
    if (currentPage > 1) {
        formPages[currentPage - 1].classList.add("hidden");
        currentPage--;
        formPages[currentPage - 1].classList.remove("hidden");
    }
}
