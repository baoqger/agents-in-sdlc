<script lang="ts">
    import GameFilter from "./GameFilter.svelte";
    import GameList from "./GameList.svelte";

    interface FilterChangeEvent {
        categoryId: number | null;
        publisherId: number | null;
    }

    let categoryId = $state<number | null>(null);
    let publisherId = $state<number | null>(null);

    const handleFilterChange = (filters: FilterChangeEvent) => {
        categoryId = filters.categoryId;
        publisherId = filters.publisherId;
    };
</script>

<div>
    <GameFilter onFilterChange={handleFilterChange} />
    <GameList {categoryId} {publisherId} />
</div>
