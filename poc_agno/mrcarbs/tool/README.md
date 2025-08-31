# Tools

### Rule:

* Any python function can be used as a tool by an Agent.
* Use the `@tool` decorator to modify what happens before and after this tool is called.

> Refrence : https://docs.agno.com/tools/tool-decorator

### BUG

There is a bug when setting `cache_results` to `True`.
When `cache_results` is set to `True`, `agno` creates a
key from the cache file from the in-coming parameters.
Then searches for the file with the same name. If file exits then it uses the contents of files i.e. cache else it makes
a call to
to the tool.
If `tool_hooks` are not set, then cache key created never matches with the existing cache file. So it thinks that there
is no cache and it proceeds to amke a call to the tool.
Even if the parameters are same, the creation of cache key before the tool call and after tool call are different.

#### File: Function
https://github.com/agno-agi/agno/blob/b746ccf9cf142cc5048e39ef71ce008d442635f3/libs/agno/agno/tools/function.py#L63

#### _build_entrypoint_args
This function returns an empty dict. 

https://github.com/agno-agi/agno/blob/b746ccf9cf142cc5048e39ef71ce008d442635f3/libs/agno/agno/tools/function.py#L520C9-L520C31

#### tool_hooks
https://github.com/agno-agi/agno/blob/b746ccf9cf142cc5048e39ef71ce008d442635f3/libs/agno/agno/tools/function.py#L640

```python
            if self.function.tool_hooks is not None:
                execution_chain = self._build_nested_execution_chain(entrypoint_args=entrypoint_args)
                result = execution_chain(self.function.name, self.function.entrypoint, self.arguments or {})
            else:
                arguments = entrypoint_args
                if self.arguments is not None:
                    arguments.update(self.arguments)
                result = self.function.entrypoint(**arguments)
```
If no `tool_hooks` are specified, it goes to `else` block and 
copies over the `self.arguments` to `arguments = entrypoint_args` 
which in result updates the `entrypoint_args`. And after the tools call
when it creates a new `cache_key` that results in different key. 



