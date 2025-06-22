import "./index.css";

import ApplicationFrame from "./components/app-frame/ApplicationFrame.svelte";
import {mount}          from 'svelte';

mount(ApplicationFrame, {target: document.body});
