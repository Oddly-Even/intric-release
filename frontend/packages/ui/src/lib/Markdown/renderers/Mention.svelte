<script lang="ts">
  import type { IntricMentionToken } from "../CustomComponents";

  type Props = {
    token: IntricMentionToken;
  };

  const { token }: Props = $props();
</script>

<!-- We have already stripped the angled brackets [[ ]] from the text; in the app we have a global class for the mention inside the question, just re-using this here. -->
<span class="question-mention">{token.handle}</span>
