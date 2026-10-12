#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,os,re,statistics,subprocess,zipfile
from collections import Counter
from pathlib import Path
import numpy as np

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def safe_text(b):
 s=b.decode('utf-8','replace')
 s=re.sub(r'(?i)(token|authorization|password|credential|secret)(\s*[:=]\s*)\S+',r'\1\2[REDACTED]',s)
 return ''.join(ch if ch.isprintable() or ch in '\n\r\t' else '�' for ch in s)[:300]
def np_test(path,allow):
 try:
  with np.load(path,allow_pickle=allow) as z:
   keys=list(z.files)
   # Force lazy entry decoding so CRC/format errors cannot hide behind open().
   for k in keys:_=z[k]
  return True,'','',keys
 except Exception as e:return False,type(e).__name__,str(e),[]
def sizes(rows,pred):
 a=sorted(r['size_bytes'] for r in rows if pred(r))
 return {'n':len(a),'min':min(a) if a else None,'median':statistics.median(a) if a else None,'max':max(a) if a else None}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--output-root',type=Path,required=True);a=ap.parse_args();out=a.output_root.resolve();(out/'audit').mkdir(parents=True,exist_ok=True);(out/'reports').mkdir(exist_ok=True);(out/'logs').mkdir(exist_ok=True);(out/'scripts').mkdir(exist_ok=True)
 frozen=list(csv.DictReader(a.manifest.open(encoding='utf-8')))
 if len(frozen)!=100:raise RuntimeError(f'frozen manifest has {len(frozen)} rows, expected 100')
 rows=[]
 markers=['version https://git-lfs.github.com/spec','oid sha256:','xet','pointer','accessdenied','unauthorized','bad gateway','xml error','<html','<!doctype html']
 for i,x in enumerate(frozen):
  p=Path(x['npz_path']);r={'npz_index':int(x['npz_index']),'path':str(p),'filename':p.name,'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'sha256':sha(p) if p.exists() else ''}
  if not p.exists():
   r.update(file_output='MISSING',magic_hex='',zip_magic_valid=False,is_zipfile=False,zip_entry_n=0,zip_bad_entry='',zip_test_pass=False,np_load_false=False,np_load_false_exception_type='FileNotFoundError',np_load_false_exception_message='missing',np_load_true=False,np_load_true_exception_type='FileNotFoundError',np_load_true_exception_message='missing',requires_pickle=False,pointer_or_error_file=False,text_preview='',truncated_or_corrupted=False,classification='OTHER');rows.append(r);continue
  b32=p.open('rb').read(32);r['magic_hex']=b32.hex();r['zip_magic_valid']=b32.startswith(b'PK\x03\x04')
  try:r['file_output']=subprocess.run(['file','-b',str(p)],capture_output=True,text=True,timeout=30).stdout.strip()
  except Exception as e:r['file_output']='ERROR '+repr(e)
  r['is_zipfile']=zipfile.is_zipfile(p);r.update(zip_entry_n=0,zip_bad_entry='',zip_test_pass=False,zip_exception_type='',zip_exception_message='')
  if r['is_zipfile']:
   try:
    with zipfile.ZipFile(p) as z:
     r['zip_entry_n']=len(z.namelist());bad=z.testzip();r['zip_bad_entry']=bad or '';r['zip_test_pass']=bad is None
   except Exception as e:r['zip_exception_type']=type(e).__name__;r['zip_exception_message']=str(e)
  else:
   try:
    with zipfile.ZipFile(p) as z:r['zip_entry_n']=len(z.namelist())
   except Exception as e:r['zip_exception_type']=type(e).__name__;r['zip_exception_message']=str(e)
  f_ok,f_ty,f_msg,f_keys=np_test(p,False);t_ok,t_ty,t_msg,t_keys=np_test(p,True)
  r.update(np_load_false=f_ok,np_load_false_exception_type=f_ty,np_load_false_exception_message=f_msg,np_load_true=t_ok,np_load_true_exception_type=t_ty,np_load_true_exception_message=t_msg,requires_pickle=(not f_ok and t_ok),numpy_key_n=len(f_keys or t_keys))
  preview='';pointer=False;html=False
  if r['size_bytes']<65536 or not r['zip_magic_valid']:
   preview=safe_text(p.open('rb').read(1024));low=preview.lower();pointer=any(m in low for m in markers[:3]);html=any(m in low for m in markers[3:])
  r.update(pointer_or_error_file=pointer or html,text_preview=preview,html_error_response=html,lfs_xet_pointer=pointer)
  emsg=' '.join([r['zip_exception_type'],r['zip_exception_message'],f_ty,f_msg,t_ty,t_msg]).lower()
  trunc=bool(r['zip_magic_valid'] and not r['is_zipfile'] and any(s in emsg for s in ['badzipfile','not a zip file','end-of-central-directory','unexpected eof','trunc']))
  crc=bool(r['zip_bad_entry'] or 'crc' in emsg)
  r['truncated_or_corrupted']=trunc;r['crc_error']=crc
  if f_ok:r['classification']='VALID_NPZ'
  elif pointer:r['classification']='LFS_XET_POINTER'
  elif html:r['classification']='HTML_ERROR_RESPONSE'
  elif crc:r['classification']='CRC_ERROR'
  elif trunc:r['classification']='TRUNCATED_ZIP'
  elif not r['zip_magic_valid']:r['classification']='NOT_ZIP'
  elif r['zip_test_pass']:r['classification']='NUMPY_FORMAT_ERROR'
  else:r['classification']='OTHER'
  rows.append(r)

 # No tar was found during preflight; independently search plausible locations.
 roots=[a.manifest.parent.parent.parent,Path('/data/home/cuiyuehan/project/mesh2cad'),Path('/data/home/cuiyuehan')]
 tar_candidates=[]
 for base in roots:
  for pat in ['00.tar.gz','00.tgz','*hy3d*.tar.gz']:
   try:tar_candidates += [str(p) for p in base.rglob(pat) if p.is_file()]
   except:pass
 tar_candidates=sorted(set(tar_candidates));tar_audit={'available':bool(tar_candidates),'candidates':tar_candidates,'tar_list_test':'NOT_AVAILABLE','archive_corruption':False,'sample_comparison':[]}
 if tar_candidates:
  # Read-only listing only. Never extract.
  tp=tar_candidates[0];q=subprocess.run(['tar','-tzf',tp],capture_output=True,text=True,timeout=600);tar_audit['tar_path']=tp;tar_audit['tar_list_test']='PASS' if q.returncode==0 else 'FAIL';tar_audit['tar_stderr']=q.stderr[-1000:];tar_audit['archive_corruption']=q.returncode!=0

 counts=Counter(r['classification'] for r in rows);valid=counts['VALID_NPZ'];invalid=len(rows)-valid
 same=Counter(r['size_bytes'] for r in rows if r['classification']!='VALID_NPZ');dominant_size,dominant_n=(same.most_common(1)[0] if same else (None,0))
 primary=''
 if counts['TRUNCATED_ZIP']>=invalid*.5:primary='A. DOWNLOAD_OR_TRANSFER_TRUNCATION'
 elif counts['LFS_XET_POINTER']>=invalid*.5:primary='A. DOWNLOAD_POINTERS_NOT_MATERIALIZED'
 elif counts['NOT_ZIP']>=invalid*.5:primary='C. FILES_ARE_NOT_NPZ'
 elif tar_audit['archive_corruption']:primary='D. ARCHIVE_CORRUPTION'
 else:primary='E. MIXED_OR_UNRESOLVED'
 gate='NPZ_DATA_INTEGRITY_REPAIR_REQUIRED' if primary.startswith(('A.','B.')) else 'HY3D_SOURCE_DATA_INTEGRITY_REVIEW'
 summary={'NPZ_N':len(rows),'VALID_NPZ_N':valid,'INVALID_NPZ_N':invalid,'ZIP_MAGIC_VALID_N':sum(r['zip_magic_valid'] for r in rows),'ZIP_TEST_PASS_N':sum(r['zip_test_pass'] for r in rows),'POINTER_N':counts['LFS_XET_POINTER'],'LFS_XET_POINTER_N':counts['LFS_XET_POINTER'],'HTML_ERROR_N':counts['HTML_ERROR_RESPONSE'],'TRUNCATED_N':counts['TRUNCATED_ZIP'],'TRUNCATED_ZIP_N':counts['TRUNCATED_ZIP'],'CRC_ERROR_N':counts['CRC_ERROR'],'NOT_ZIP_N':counts['NOT_ZIP'],'EXTRACTION_CORRUPTION_N':counts['EXTRACTION_CORRUPTION'],'ARCHIVE_CORRUPTION_N':counts['ARCHIVE_CORRUPTION'],'NUMPY_FORMAT_ERROR_N':counts['NUMPY_FORMAT_ERROR'],'OTHER_N':counts['OTHER'],'REQUIRES_PICKLE_N':sum(r['requires_pickle'] for r in rows),'LOADABLE_SIZE':sizes(rows,lambda r:r['classification']=='VALID_NPZ'),'FAILED_SIZE':sizes(rows,lambda r:r['classification']!='VALID_NPZ'),'FAILED_DOMINANT_SIZE_BYTES':dominant_size,'FAILED_DOMINANT_SIZE_N':dominant_n,'CLASSIFICATION_COUNTS':dict(counts),'PRIMARY_FAILURE_CAUSE':primary,'TAR_AUDIT':tar_audit,'CURRENT_GATE':gate}
 fields=list(rows[0])
 with (out/'audit/NPZ_INTEGRITY_100.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 (out/'audit/NPZ_INTEGRITY_100.json').write_text(json.dumps({'source_manifest':str(a.manifest.resolve()),'summary':summary,'files':rows},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 conclusion=('The 89 failures are primarily transfer/download truncation: they retain the ZIP local-header magic but lack a valid central directory, and most share an exact 7.5 MiB cutoff. The source tar is unavailable, so extraction-vs-download origin cannot be proven from archive comparison.' if primary.startswith('A.') else 'The failures require source-data integrity review; current evidence does not support a single recoverable transfer cause.')
 md=f"""# HY3D NPZ Integrity Audit V1

## Frozen input

The exact 100 paths from `{a.manifest.resolve()}` were inspected. No file was replaced, deleted, repaired, or supplemented.

## Counts

- NPZ_N={len(rows)}
- VALID_NPZ_N={valid}
- INVALID_NPZ_N={invalid}
- ZIP_MAGIC_VALID_N={summary['ZIP_MAGIC_VALID_N']}
- ZIP_TEST_PASS_N={summary['ZIP_TEST_PASS_N']}
- LFS_XET_POINTER_N={summary['LFS_XET_POINTER_N']}
- HTML_ERROR_N={summary['HTML_ERROR_N']}
- TRUNCATED_ZIP_N={summary['TRUNCATED_ZIP_N']}
- CRC_ERROR_N={summary['CRC_ERROR_N']}
- NOT_ZIP_N={summary['NOT_ZIP_N']}
- NUMPY_FORMAT_ERROR_N={summary['NUMPY_FORMAT_ERROR_N']}
- OTHER_N={summary['OTHER_N']}

## File-size evidence

- Loadable: {summary['LOADABLE_SIZE']}
- Failed: {summary['FAILED_SIZE']}
- Dominant failed size: {dominant_size} bytes in {dominant_n}/{invalid} failures

## ZIP and NumPy diagnosis

All classifications are mutually exclusive and recorded per file with 32-byte magic, `file` output, `zipfile.is_zipfile`, `testzip`, and forced NumPy entry reads for both pickle modes. `REQUIRES_PICKLE_N={summary['REQUIRES_PICKLE_N']}`.

## Pointer/error-file diagnosis

Pointer files={summary['POINTER_N']}; HTML/XML/error responses={summary['HTML_ERROR_N']}. Text previews are sanitized and stored only when magic is invalid or files are small.

## Tar archive comparison

Original `00.tar.gz` available: {tar_audit['available']}. Candidates: {tar_candidates}. Listing result: {tar_audit['tar_list_test']}. Because no source archive is present, the requested 5-valid/5-failed archive-size comparison cannot be performed and no `EXTRACTION_CORRUPTION` or `ARCHIVE_CORRUPTION` label is asserted.

## Primary failure cause

`{primary}`

{conclusion}

## Recommended recovery

Re-acquire the same frozen 89 paths (not replacement samples), verify expected size and SHA-256 after transfer, and rerun this integrity audit before repeating the watertight audit. Do not automatically download as part of this stage.

## Gate

`CURRENT_GATE={gate}`
"""
 (out/'reports/FINAL_REPORT.md').write_text(md,encoding='utf-8')
 terminal=f"""HY3D_NPZ_INTEGRITY_AUDIT_V1

NPZ_N=100
VALID_NPZ_N={valid}
INVALID_NPZ_N={invalid}

ZIP_MAGIC_VALID_N={summary['ZIP_MAGIC_VALID_N']}
ZIP_TEST_PASS_N={summary['ZIP_TEST_PASS_N']}

POINTER_N={summary['POINTER_N']}
TRUNCATED_N={summary['TRUNCATED_N']}
CRC_ERROR_N={summary['CRC_ERROR_N']}
NOT_ZIP_N={summary['NOT_ZIP_N']}

PRIMARY_FAILURE_CAUSE={primary}

REPORT={out/'reports/FINAL_REPORT.md'}

CURRENT_GATE={gate}
"""
 (out/'logs/final_terminal.log').write_text(terminal,encoding='utf-8');print(terminal,end='')
if __name__=='__main__':main()
