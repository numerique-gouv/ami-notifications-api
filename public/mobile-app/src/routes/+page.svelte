<div>
    <h1>Welcome to the Mobile App</h1>
    
Bouton pour accepter les notifyMessage
Les 3 champs disabled) en console.log
Email for registration

    {#if form?.error}
        <p class="error">{form.error}</p>
    {/if}

    <form 
        method="POST"
        action="?/notifyMessage"
        use:enhance={() => {
            creating = true;

            return async ({ update }) => {
                await update();
                creating = false;
            };
        }}
    >
        <p>
            <label>User to notify
                <input
                    type="text"
                    name="user-email"
                    value={form?.userEmail ?? ''}
                    disabled={creating}/>
            </label>
        </p>
        <p>
            <label>Message to notify
                <input
                    type="text"
                    name="notify-message"
                    value={form?.notifyMessage ?? ''}
                    disabled={creating}/>
            </label>
        </p>
        <p>
            <button id="notify-message">Notify me</button> 
            <span id="notify-message-status"></span>
        </p>

        {#if creating}
            <span class="saving">Notifying...</span>
        {/if}
    </form>
</div>

<script lang="ts">
    import { enhance } from '$app/forms';

    let { data, form } = $props();

	let creating = $state(false);
</script>

<style>
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
