document.addEventListener('DOMContentLoaded', () => {
    const newsContainer = document.querySelector('.news-container');
    const loadingSpinner = document.getElementById('loading');
    let currentPage = 1;
    let isLoading = false;
    let noMoreData = false;

    async function fetchNews(page) {
        if (isLoading || noMoreData) return;
        isLoading = true;
        loadingSpinner.style.display = 'block';

        try {
            const response = await fetch(`/fetch_news?page=${page}`);
            const data = await response.json();

            loadingSpinner.style.display = 'none';
            isLoading = false;

            if (!data.length) {
                noMoreData = true;
                if (!document.querySelector('.end-message')) {
                    const endMessage = document.createElement('div');
                    endMessage.classList.add('end-message');
                    endMessage.textContent = 'No more news to load.';
                    newsContainer.appendChild(endMessage);
                }
                return;
            }

            data.forEach(news => {
                const newsArticle = document.createElement('div');
                newsArticle.classList.add('news-article');
                newsArticle.innerHTML = `
                    <h3>${news.title}</h3>
                    <p class="news-content">${news.content}</p>
                    <span class="source">Source: ${news.source}</span>
                    <span class="time">Date: ${news.time}</span>
                    <span class="read-more" onclick="toggleContent(this)">Show More</span>
                `;
                newsContainer.appendChild(newsArticle);
            });
        } catch (error) {
            console.error('Error fetching news:', error);
            loadingSpinner.style.display = 'none';
            isLoading = false;
        }
    }

    window.toggleContent = function (button) {
        const newsArticle = button.closest('.news-article');
        const content = newsArticle.querySelector('.news-content');

        content.classList.toggle('show');
        newsArticle.classList.toggle('show-more');

        button.textContent = content.classList.contains('show') ? 'Show Less' : 'Show More';
    };

    let debounceTimeout;
    window.addEventListener('scroll', () => {
        if (debounceTimeout) clearTimeout(debounceTimeout);

        debounceTimeout = setTimeout(() => {
            if (
                window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
                !isLoading &&
                !noMoreData
            ) {
                currentPage++;
                fetchNews(currentPage);
            }
        }, 200);
    });

    fetchNews(currentPage); // Initial fetch
});
