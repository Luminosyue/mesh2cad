"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_006.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_006.stl', 'source_sha256': '431131b91712018df6eca794ce48e0f7d040e4f64326bd4092103fe0da925a34', 'input_faces': 272, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.134582981467247, 0.08965182304382324, 0.024341072887182236], [0.32752928137779236, 0.3630596101284027, 0.253589391708374]]}
GEOMETRY_BASE85 = 'c$}q~2~btn8OM);Chn-jtyLdtKwKj(C}_N{QE|b#f$Kv-F`}&Ef|}<pqOl4^#h?!mqfXScN!&`zbw#BJRf`&pzD^P|omex8)yYhq*mu6~f4%n}$xNqxGvEAw_y6wu&bjBDdlra{@bUE*{0R`(3U-c&@)JTvec><C<5JS*&xuRzwkT;?4dF+={1}=&cG8&0=o%tjWCX>=rOrtS3UdVYpW8R6iz8@mVoF*{%%WL|DY0?VA0CsC8t3&><71NIyw@Fj^y$~d(KEP<W2NJN{M7YU!Q&HlcA!_?WtXl?bsY0MFVz`%n*IBY&d_z|W|dN157~De?^GgHRD_Z5j=V^|=U_v+Uk_SdPWgIXB3~ptIZpS5`c}~Q9m?3xiatsC+VK72)HPckEvi=;<=Jx6cE7%zecf}%R!>Lpn#*)w^gUa-&UJ^cP`(%U?DhYtFWv9S>2!{+`#t(AeLp6v)apBD7Th2|pv&h}?)nhEe{nMTqH+hdoA!X)&-3wz)Sj*(pOspD*Vyoz^!=R&R9{#00rs6=Qy#~WfADqt`4{NEk`VGe<2IFAeXV5<<<av->2w`=n|zl~PpZG;+sS2C-*IRvm)j)gGy2`aaTn>iR>$)1@BL!)#ge1^9CuvQ-dgeu@?DYjD31tuo$`vQnS6iQb1GN6+`G)`J9|B(`?bpZC&<5ftJ?gIw4d1jaVhs>RihHC@A-5K_j9c;k6C@kq7Bp!`i<>ptiJ1T6}N{-{1fS>7hIn{OSwHO>y=u4;o3{}bk^|Y@sXW$iSm`~;{4@3&RBid^b3?<uU$d;oi8?As;+&Uy?2nWjm@X=p!MB#)#`gT2LFwI7rXd0ec!HWDUaVRR8Qwyg_o?pbH--w_kxA|p42{BT3xw@uN4MYkro%zb83k?`FiYnZr{c`b*nE9aytvZ+h=Wl2HJUHez7f2QYH7p{DQ;eAHT}wc6`p`e|PQ`tFJF@Mb9h7KcVtny8`I_bNz6X%MDz0*6KTgk5Yc!ug*twJ-jQw-w)l?K3YtlOIBa2T+Ho|%=3cb>!Dw8JAZql)Rw1R4!6(KbQ+J2@q5`{7r^=VUB7Jgogq)T{o|JNc-w!6>p$uQ&4c>m2jx~@%&wyQT`yLDO#c0T)E<s&o9TUV>sjSiU+WP?^>jZ7`GkJIaS8kT-r@P@MBU3)Uo@|v{O(q@besQU9Oco&4_>kQdi+1>c|CgzxqW(H<?sLAkNV4ft>7<KUwgWR@_0gLALsG3h{msH;CEc!_nGIdzT@l8bS->7%D4LZ?ZrIapWi8>axSKlFaC9i$`w_^%B;S2E`iF`e$GBc-!CZQ{679X53Ke-Z}nYojHLX|!ecZ(U4h?`?|%9v<=6G0SFOIThx0gWpZjOhNi%qzso#LwS^s6g6|1iuuEXtcpy+d}@0rn=^Q^sl)#{7qLANN+ltgMLmrpkL^OPfW?XC#8VD+`fU-5f5z3{x%_msuawf@zkT~=Rzv5KD8{cKs0)pwme#`DFy%L}Z&xR*ua({u6sHCws&XY)85Jj3R@TQ;Y5^Jr1!w)_LP@_W7DUYV_)6VGu!KDl_+R?kB}lka@Y<M3sk${O6iMQKND{=b{?_)i&b%kQq=hTq@P@)BEnj-JT<lAm+h_PhZu&U1I$A8qwX&*VJib5GjJEjh;Zneg;eTl*;Ur{Ozi_NV?8@xI)j!B;A(8$X7xjvvEU$B*Hw<3~$sTUp(BHhgtF>zRWpt9xGzUwvP6M|5R%@1x<X@1yp38t2Igqw*Y&Mx3+yugnkdUzs1^tMh~2;V9QfnU@S-otN~CTkI?Iq~WXc<V#<fCk<bnCtd!}xc<t#ZTRZE?dlQ8`$%P7Fno1g5O;^LudF+UudX}V2P^n~WgRqpbsaQ(bsc<}M_C6&>Kd-UvMw9Gx-M(q9N}`+bsxUE?z><6gneZnV)*Jl<fX6dLtf@l_933|6I_3FUj+Y^ebLc6Jnq$f7kqW!<?b+w_jAg=&hXWJoxXP5_3G-QpPI_&E@hu-`075>k&(^yQTDNhukK^DT6yd%`)b2i_tl24?yC)7-B&v&@j2&}^TLj6>?`L2!&lD*`i5_+Z6D{R@A-b^oMQN|l-oRr-+%QS1pk$DQ1VP}N9CMl`06=Julj=XE9W)6qAurE&V7cjp8K57m+^Bd=SOjBCHu-b)bQ1FsB^$Gp4Y7B_ek4cB{rV^!B=bGeH3rh5&mLsjO9-f(v%-VtN)Y4{9ganpCm#;L;l}CNi6i%VZAptASCBPbHKUaeCP+@eDF@_AHX}oo1h!Po4`rXL~s&#0(3lh0(dBN2zV&CE3^x^E4U5xx8OG5X3#gl&A_dpzX7)fcZPNXOC1bOmt(>ks}Pbip_{>(;FZw#z$?M2(8b_X@Em9ycn&xkIt?5Rj)0B<M}Yf7-v;*whd_IQL%<!O!QhVIp3vUlp5Ot{f#3n)(a^Er(ctOO+2HBmSm<1EEI19C4o*i~OWy5`t=?DyO$ILkPl8ScPXdQQHE<ZX1+)XW1-K!!F}NYP0n`uN0Ne=L1l$PR68a{%B{<w0Gogc^Z-NJbyCWn!piRIIaC4|1xH-5jv@y6XxEr(sxEpvFR09tKPk~MbPXRB0CW9A%*Fv{~*MfH-B)g%z!ESJoHx5AeLU)7rf|o&;fR}+MLMMSIg8M?lz<t3@p)J5o!S$dG!S%obis_p^lIueof$M|)p)JAw;C|3>a6j-=VUCHZ2+7O6u@AZwIupDU?1T;iJHf-D-NB=vq0sK&P;d~`0S*GUhc*Yd2M0pif&;;QpxwZIz$2l<z$3v?&?(?3@I2@O@H}t^bS*dooCVzh&H`^kNZtc=gZF?7p+(?AaIrAQWij+1xEQ=2`XP8fI1joHybpbrhmf2Cb%ImCv!KJlM*q!1NS+~hE|oeOI!c&xujB#HP+`v1l6yjfggLiM?g(u!%(Xyr2sBWbYlr0i&_2RkYa~ZNM+$Rok{k_<66RVac@A`*FxNiGsn85zu9cEkLbHUqwo1-~ZWHEOEZJB;q;7$3154cl-U7~s7J{?E1<+z}G5WgzA^Cl19ykyE`aVK(0(2I57Wyv%AvxaC$MMiua6EVgG!2}FXIKHv2Co3GgBE}bP^Wd!1aJb%ki5nl+l9HulbjFTCCojc<Xq_Qg}H~6yaBpen0rpii=gwti@@Wck>GLQ!O(ZWgTbAlZ-G05TSEhcxyO^-4BASVdqT-=pzVaYhm_nE+C!LoPRT=|BZRp}l{^9ZJ7Ml=B_~1O73LmT@+RmS@EWwWWVsiL5xfsd2fGlGHzOp!hmgD&Avq2qc^X3U7=+}v5t4f$BnKlT_eMw_h>$!MA$c}*E?AB|IgaFbs_Bgy-tdL`fPKNWyz!bhY72RYVtpN42Q2@e8W~ZeroYdx{Y%*VxMU%=e-Nv`v>)57zs&XKdU=S8jHo5+;(dUcw83dCM~3(h#fCRy'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
