# Vtable and vptr (C++ — level9)

## Concept
In C++, virtual calls go through a **function table** (vtable) pointed to by a **vptr** field in the object. The call is `(*(obj->vptr)[index])(args)`. If we control **vptr** (overflow), we control the address called.

## Simple definition
- Every object with virtual methods has a **vptr** (often at offset 0) pointing to the vtable.
- The vtable is an array of function pointers. First virtual call = *(vptr+0).
- In asm: `mov eax, [obj]` (eax = vptr), `mov edx, [eax]` (edx = address to call), `call edx`.

## Where it appears (level9)
- Two **N** objects (0x6c bytes each), allocated next to each other. First: vptr at +0, annotation at +4. Second = first+0x6c, its vptr at offset 0 of second.
- **setAnnotation(first, argv[1])**: memcpy(first+4, argv[1], strlen(argv[1])) **with no bound** → overflow to the second object.
- Offset to reach the second's vptr: 4 (first vptr) + 100 (annotation) + 4 (member) = **108** bytes.

## Diagram

```
  first                      second
  +------+                   +------+
  | vptr |  +0               | vptr |  ← we overwrite here with first+4
  +------+                   +------+
  | annot|  +4  ... overflow |
  +------+                   +------+
  ...
  Offset 108 = start of second's vptr
```

## Exploit
- We put **first+4** in second->vptr (last 4 bytes of the payload).
- At the call: *(second->vptr) = *(first+4) = **the first 4 bytes of our payload** = shellcode address (that we put there).
- So the call jumps to the shellcode (e.g. in env).

## Mental summary
vptr = pointer to the vtable. Overflow to replace vptr with an address we control; *(that address) = address of the function called → we put the shellcode address.

**See also:** `concepts.md` for the full exploit chain, heap layout, GDB, payload.

## References
- Itanium C++ ABI (vtable/vptr): https://itanium-cxx-abi.github.io/cxx-abi/abi.html#vtable
