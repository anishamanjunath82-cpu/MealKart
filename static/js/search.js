/* mealKart - Live Header Search and Home Filtering */

document.addEventListener('DOMContentLoaded', function() {
    // --- Global Live Navbar Search ---
    const searchInput = document.getElementById('global-search-input');
    const searchDropdown = document.getElementById('search-dropdown-results');

    if (searchInput && searchDropdown) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();

            if (query.length < 2) {
                searchDropdown.innerHTML = '';
                searchDropdown.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        const results = data.results;
                        searchDropdown.innerHTML = '';

                        if (results.length === 0) {
                            searchDropdown.innerHTML = '<div class="search-no-results">No food items or restaurants found</div>';
                        } else {
                            results.forEach(item => {
                                const resultRow = document.createElement('a');
                                resultRow.href = `/hotel/${item.hotel_id}/`;
                                resultRow.className = 'search-result-item';

                                const vegBadge = item.is_veg 
                                    ? '<span class="badge-veg"><i class="fa-solid fa-leaf"></i> Veg</span>' 
                                    : '<span class="badge-nonveg"><i class="fa-solid fa-drumstick-bite"></i> Non-Veg</span>';

                                resultRow.innerHTML = `
                                    <img src="${item.image}" alt="${item.name}" class="search-result-img" onerror="this.src='/static/images/default_food.jpg'">
                                    <div class="search-result-details">
                                        <div class="search-result-title-row">
                                            <span class="search-result-name">${item.name}</span>
                                            <span class="search-result-price">₹${item.price.toFixed(0)}</span>
                                        </div>
                                        <div class="search-result-meta-row">
                                            <span class="search-result-hotel">${item.hotel_name}</span>
                                            <span class="search-result-rating"><i class="fa-solid fa-star"></i> ${item.rating.toFixed(1)}</span>
                                        </div>
                                        <div style="margin-top: 4px;">${vegBadge}</div>
                                    </div>
                                `;
                                searchDropdown.appendChild(resultRow);
                            });
                        }
                        searchDropdown.classList.remove('hidden');
                    })
                    .catch(err => {
                        console.error('Error fetching search results:', err);
                    });
            }, 300);
        });

        // Hide search when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.classList.add('hidden');
            }
        });

        // Show search results again on focus if input is filled
        searchInput.addEventListener('focus', function() {
            if (searchInput.value.trim().length >= 2 && searchDropdown.children.length > 0) {
                searchDropdown.classList.remove('hidden');
            }
        });
    }

    // --- Home Category Filter Action ---
    const categoryBubbles = document.querySelectorAll('.category-bubble');
    const hotelCards = document.querySelectorAll('.hotel-card');

    if (categoryBubbles.length > 0) {
        categoryBubbles.forEach(bubble => {
            bubble.addEventListener('click', function() {
                // Toggle active state of bubbles
                categoryBubbles.forEach(b => b.classList.remove('active'));
                bubble.classList.add('active');

                const catId = bubble.getAttribute('data-category-id');
                const catName = bubble.getAttribute('data-category-name') || '';

                const filteredSection = document.getElementById('filtered-foods-container');
                const filteredTitle = document.getElementById('filtered-section-title');
                const filteredGrid = document.getElementById('filtered-foods-grid');
                
                const trendingSec = document.querySelector('.trending-section');
                const combosSec = document.querySelector('.combos-section');
                const hotelsSec = document.querySelector('.hotels-section');

                if (!catId) {
                    // "All Foods" selected, restore normal view
                    if(filteredSection) filteredSection.classList.add('hidden');
                    if (trendingSec) trendingSec.classList.remove('hidden');
                    if (combosSec) combosSec.classList.remove('hidden');
                    if (hotelsSec) hotelsSec.classList.remove('hidden');
                    return;
                }

                // A specific category is selected
                if (trendingSec) trendingSec.classList.add('hidden');
                if (combosSec) combosSec.classList.add('hidden');
                if (hotelsSec) hotelsSec.classList.add('hidden');
                
                if(filteredTitle) filteredTitle.innerHTML = `${catName} Varieties`;
                if(filteredGrid) filteredGrid.innerHTML = '<div class="search-no-results">Loading delicious items...</div>';
                if(filteredSection) filteredSection.classList.remove('hidden');

                // Fetch foods for this category
                fetch(`/api/search/?category=${catId}`)
                    .then(res => res.json())
                    .then(data => {
                        if(filteredGrid) {
                            filteredGrid.innerHTML = '';
                            if (data.results.length === 0) {
                                filteredGrid.innerHTML = '<p>No items found for this category.</p>';
                                return;
                            }
                            
                            data.results.forEach(item => {
                                const vegClass = item.is_veg ? 'veg' : 'non-veg';
                                const heartClass = item.is_favorite ? 'solid liked' : 'regular';
                                
                                const card = document.createElement('div');
                                card.className = 'trending-card glass-panel fade-in';
                                card.innerHTML = `
                                    <div class="trending-img-wrapper">
                                        <img src="${item.image}" alt="${item.name}" onerror="this.src='/static/images/default_food.jpg'">
                                        <span class="veg-badge ${vegClass}"></span>
                                        <button class="favorite-heart-btn ${item.is_favorite ? 'liked' : ''}" data-food-id="${item.id}">
                                            <i class="fa-${heartClass} fa-heart"></i>
                                        </button>
                                    </div>
                                    <div class="trending-details">
                                        <div class="trending-meta">
                                            <span class="food-category-tag">${item.category_name}</span>
                                            <div class="food-rating"><i class="fa-solid fa-star"></i> ${item.rating.toFixed(1)}</div>
                                        </div>
                                        <h4>${item.name}</h4>
                                        <p class="hotel-owner">By <a href="/hotel/${item.hotel_id}/" style="color: inherit; text-decoration: none;">${item.hotel_name}</a></p>
                                        <div class="trending-price-action">
                                            <span class="price">₹${item.price.toFixed(2)}</span>
                                            <button class="btn-add-to-cart" data-food-id="${item.id}">
                                                <span class="plus-icon">+</span> Add
                                            </button>
                                        </div>
                                    </div>
                                `;
                                filteredGrid.appendChild(card);
                            });
                        }
                    })
                    .catch(err => {
                        if(filteredGrid) filteredGrid.innerHTML = '<p>Error loading items.</p>';
                    });
            });
        });
        
        // Setup Clear Filters Button
        const clearBtn = document.getElementById('clear-filters-btn');
        if(clearBtn) {
            clearBtn.addEventListener('click', () => {
                const allFoodsBubble = document.querySelector('.category-bubble[data-category-id=""]');
                if(allFoodsBubble) allFoodsBubble.click();
            });
        }
    }
});
