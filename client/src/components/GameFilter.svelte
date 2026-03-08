<script lang="ts">
    import { onMount } from "svelte";

    interface Category {
        id: number;
        name: string;
    }

    interface Publisher {
        id: number;
        name: string;
    }

    interface FilterChangeEvent {
        categoryId: number | null;
        publisherId: number | null;
    }

    let {
        onFilterChange
    }: {
        onFilterChange: (filters: FilterChangeEvent) => void;
    } = $props();

    let categories = $state<Category[]>([]);
    let publishers = $state<Publisher[]>([]);
    let selectedCategoryId = $state<number | null>(null);
    let selectedPublisherId = $state<number | null>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    const fetchFilters = async () => {
        loading = true;
        try {
            const [categoriesResponse, publishersResponse] = await Promise.all([
                fetch('/api/categories'),
                fetch('/api/publishers')
            ]);

            if (categoriesResponse.ok && publishersResponse.ok) {
                categories = await categoriesResponse.json();
                publishers = await publishersResponse.json();
            } else {
                error = "Failed to load filter options";
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const handleCategoryChange = (event: Event) => {
        const target = event.target as HTMLSelectElement;
        selectedCategoryId = target.value ? parseInt(target.value) : null;
        onFilterChange({
            categoryId: selectedCategoryId,
            publisherId: selectedPublisherId
        });
    };

    const handlePublisherChange = (event: Event) => {
        const target = event.target as HTMLSelectElement;
        selectedPublisherId = target.value ? parseInt(target.value) : null;
        onFilterChange({
            categoryId: selectedCategoryId,
            publisherId: selectedPublisherId
        });
    };

    const handleClearFilters = () => {
        selectedCategoryId = null;
        selectedPublisherId = null;
        onFilterChange({
            categoryId: null,
            publisherId: null
        });
    };

    onMount(() => {
        fetchFilters();
    });
</script>

<div class="mb-8 p-6 bg-slate-800 rounded-xl shadow-lg border border-slate-700">
    <h3 class="text-lg font-medium mb-4 text-slate-100">Filter Games</h3>
    
    {#if loading}
        <div class="text-slate-400">Loading filters...</div>
    {:else if error}
        <div class="text-red-400">{error}</div>
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Category Filter -->
            <div>
                <label for="category-filter" class="block text-sm font-medium text-slate-300 mb-2">
                    Category
                </label>
                <select
                    id="category-filter"
                    data-testid="category-filter"
                    value={selectedCategoryId?.toString() ?? ""}
                    onchange={handleCategoryChange}
                    class="w-full px-4 py-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                >
                    <option value="">All Categories</option>
                    {#each categories as category (category.id)}
                        <option value={category.id}>{category.name}</option>
                    {/each}
                </select>
            </div>

            <!-- Publisher Filter -->
            <div>
                <label for="publisher-filter" class="block text-sm font-medium text-slate-300 mb-2">
                    Publisher
                </label>
                <select
                    id="publisher-filter"
                    data-testid="publisher-filter"
                    value={selectedPublisherId?.toString() ?? ""}
                    onchange={handlePublisherChange}
                    class="w-full px-4 py-2 bg-slate-700 text-slate-100 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                >
                    <option value="">All Publishers</option>
                    {#each publishers as publisher (publisher.id)}
                        <option value={publisher.id}>{publisher.name}</option>
                    {/each}
                </select>
            </div>

            <!-- Clear Filters Button -->
            <div class="flex items-end">
                <button
                    onclick={handleClearFilters}
                    data-testid="clear-filters"
                    class="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg transition-colors duration-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                    Clear Filters
                </button>
            </div>
        </div>
    {/if}
</div>
