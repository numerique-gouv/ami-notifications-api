<!-- <h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to read the documentation</p>

<form method="POST" action="?/notifyMessage">
    <p><label>Message to notify <input type="text" id="notify-message-input"/></label></p>
    <p><button type="button" id="notify-message">Notify me</button> <span id="notify-message-status"></span></p>
</form> -->


<script>
	let { data } = $props();
</script>

<div class="centered">
	<h1>todos</h1>

    <form method="POST" action="?/create">
        <label>
            add a todo:
            <input
                name="description"
                autocomplete="off"
            />
        </label>
    </form>

	<ul class="todos">
        {#each data.todos as todo (todo.id)}
            <li>
                <form method="POST" action="?/delete">
                    <input type="hidden" name="id" value={todo.id} />
                    <span>{todo.description}</span>
                    <button aria-label="Mark as complete"></button>
                </form>
            </li>
        {/each}
    </ul>
</div>

<style>
	.centered {
		max-width: 20em;
		margin: 0 auto;
	}

	label {
		width: 100%;
	}

	input {
		flex: 1;
	}

	span {
		flex: 1;
	}

	button {
		border: none;
		background: url(./remove.svg) no-repeat 50% 50%;
		background-size: 1rem 1rem;
		cursor: pointer;
		height: 100%;
		aspect-ratio: 1;
		opacity: 0.5;
		transition: opacity 0.2s;
	}

	button:hover {
		opacity: 1;
	}
</style>
