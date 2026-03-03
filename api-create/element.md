#step1: enter create api page & start create process
- url: https://app.fireworks.ai/settings/users/api-keys
- button element: 


- button outhtml
<button class="font-medium inline-flex content-center items-center whitespace-nowrap cursor-pointer ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 transition-[transform,background-color,color] [&amp;.state-enabled]:active:translate-y-0.5 font-nunitoSans focus-visible:ring-primary [&amp;.state-disabled]:cursor-not-allowed rounded-md bg-black text-white [&amp;.state-enabled]:hover:bg-gray-800 [&amp;.state-disabled]:text-gray-500 [&amp;.state-disabled]:bg-gray-100 [&amp;.state-disabled]:border-gray-300 [&amp;.state-disabled]:border text-paragraph-sm h-10 px-6 state-enabled gap-2 justify-center" type="button" id="radix-_r_k_" aria-haspopup="menu" aria-expanded="true" data-state="open" data-sentry-element="DropdownMenuButtonTrigger" data-sentry-source-file="AddNewKeyModal.tsx" aria-controls="radix-_r_l_"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-plus h-3 w-3" data-sentry-element="Plus" data-sentry-source-file="AddNewKeyModal.tsx"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>Create API Key<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down h-4 w-4"><path d="m6 9 6 6 6-6"></path></svg></button>

- apikey create button
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-key h-4 w-4"><path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"></path><path d="m21 2-9.6 9.6"></path><circle cx="7.5" cy="15.5" r="5.5"></circle></svg>


- key step:
1. click the button
2. choose the "API key" from the list

#step2: enter API name

create random name and fill in

- element:
<div class="my-4 flex flex-col gap-4"><div data-sentry-component="FieldLabel" data-sentry-source-file="FormFields.tsx"><label class="font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex flex-col gap-3" for="name" data-sentry-element="Label" data-sentry-source-file="FormFields.tsx"><span class="flex items-center"><span>API Key Name</span><span class="shrink-0">*</span></span></label><div class="relative"><input class="focus:ring-input-active focus:border-input-active focus:ring-inset border-gray-300 bg-input h-10 w-full rounded-md border px-3.5 py-2 file:border-0 file:bg-transparent disabled:cursor-not-allowed disabled:opacity-50 mt-2.5 pl-3 pr-3" id="name" aria-required="true" aria-invalid="false" placeholder="Enter a name" type="text" name="name"></div></div></div>

key step: enter API name and continue next


- click "Generate Key" button
<button class="font-bold whitespace-nowrap rounded cursor-pointer ring-offset-background focus-visible:outline-none focus-visible:ring-offset-2 transition-[transform,background-color,color] not-disabled:active:translate-y-0.5 leading-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed bg-primary-500 text-black disabled:bg-gray-500 disabled:text-gray-700 [&amp;:not(:disabled)]:hover:bg-primary-800 [&amp;:not(:disabled)]:focus:bg-primary-800 h-10 px-6 [&amp;:not(.button--link)]:text-md font-nunitoSans inline-flex items-center justify-center" type="submit" data-sentry-element="Element" data-sentry-component="UnwrappedButton" data-sentry-source-file="Button.tsx">Generate Key</button>


#step3: extract API key and save 

Element: <p class="text-lg">API Key: <code class="rounded border border-border px-1.5 py-0.5 font-nunitoSans mx-2 text-md" data-sentry-component="InlineCode" data-sentry-source-file="InlineCode.tsx">fw_Y3sMPwpfgDjL8UFUimAVQL</code> <button class="font-bold whitespace-nowrap rounded cursor-pointer ring-offset-background focus-visible:outline-none focus-visible:ring-offset-2 transition-[transform,background-color,color] not-disabled:active:translate-y-0.5 focus-visible:ring-2 focus-visible:ring-primary aspect-1 min-w-max disabled:cursor-not-allowed bg-secondary-1000 text-secondary-300 disabled:bg-gray-500 disabled:text-gray-700 [&amp;:not(:disabled)]:hover:bg-secondary-900 [&amp;:not(:disabled)]:focus:bg-secondary-900 h-8 text-sm font-nunitoSans inline-flex items-center justify-center" type="button" aria-label="Copy to clipboard" data-sentry-element="Element" data-sentry-component="UnwrappedIconButton" data-sentry-source-file="IconButton.tsx"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy h-4 w-4" aria-hidden="true" data-sentry-element="Copy" data-sentry-source-file="CopyToClipboard.tsx"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg></button></p>

key steps: extract from the page the API key and save to json.


