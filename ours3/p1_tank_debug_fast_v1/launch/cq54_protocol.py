CHUNK_TOKENS=1024
PREFIX_TOKENS=384
END_MARKER='# CAD_COMPLETE'
def prompt_for(tokenizer,prefix,index):
    ids=tokenizer.encode(prefix,add_special_tokens=False)
    suffix=tokenizer.decode(ids[-PREFIX_TOKENS:],skip_special_tokens=False) if ids else '(start of program)'
    return ('<point_cloud>\nWrite the next block of a CadQuery Python program for this geometry. '
            'Output only the new code block, without markdown or repeating the prefix. '
            'The program begins with import cadquery as cq and assigns the final shape to result. '
            'Do not export files. Blocks join with a newline. Append # CAD_COMPLETE only when the whole program is finished.\n'
            f'Block index: {index}\nRecent generated code:\n'+suffix+'\nContinue with the next block:')
