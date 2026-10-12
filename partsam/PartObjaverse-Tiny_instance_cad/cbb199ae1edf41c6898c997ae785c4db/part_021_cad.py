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

PART_NAME = 'part_021'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_021.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_021.stl', 'source_sha256': '8b5f00bb8a053bdbc47a39e065c9806a4dbe5150ff0e8c3ce70dd5482b3d9fa8', 'input_faces': 284, 'input_vertices': 235, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49997398257255554, -0.30700135231018066, -0.1885155439376831], [0.19273820519447327, 0.1283165067434311, 0.1979115903377533]]}
GEOMETRY_BASE85 = 'c$}r0c~n)`6~?b~TeUHbwTa_JOi=4kM;xNu#<5xxjN(u+K2TJg1tVZYuSuQKR-zzA<8YOzb%+CK6mfVWlZq9^Xl-hI;(+mw{?XOdwVI@%=bZcPn|n7mYjw4(wb%E(-`RV=ea}5_fJOA^di9%Y_D`5r-g9itx)z!yqlwmBTbhuxByoB|a<>JG(&}i<6qi4wnXku;iJn|XTdKViF(V;)dQ!vyJ>u1w{UW;P5i=JiElG-7Fl}Mdj0DMt$IVMl5IlKy+@b{WxMR;=eY)tqI(5<0_5bnbM`DD~rkeW~ga(3dT$dW0KJ)wq7dMEHXrJrm`ni8yQ;%7`Mx5nq2Uiy>jePr}n}-hAJTx-io4>z%k#GJ!n^V5E>7G5$ld(6|oFfnV^1$kEj=H&7clkEef0Q@hAimDd4{RLoyFbMF{t)N;L!9rA!`c22=lkR2v;A@M+5YGod;0DV=d?e>`Th{+`(vyx_+0gkKC>@M_8IeSo*xg5`dhAt57~W6a*OAK>!a;_b6tvWf6l4D!&!gMslR2`+)?~Vy4nY;uf3ndP4K|bE5|(iLH`OhcmK78e%$Px5Oi}b*hZZbW8k<;emu~(hxd8UoGMqG_XoFF|4@Fi;-NtaMZTO}mj!OI>k6ETyQ-AUN!(;}THPBLsPi${`@A~1G0fXvJ8^cR>c{dm)8?W6sbizu*Bdz|S3PF=Mn9YD?Y;TNxUT2bd6@9+DbM`{x0-$P@4;?<cwSI)BmM9}&%S{NBEMGo`pWV4oL}y(RCBdDR2b#rp{F*tB5F$AJW&1BO}~5tJlHwrvYYdBNSvQThd+GnhT^P$0NiBrXjNM({PIH&Y;Li6_&MjC&biZ{opa9VoI8EkIp^GB{rPz&&d;;659~a1ZnAm!c_z-!vvXbSJUg77XXm=ud3MeNJJ05dhBmJ{?YUpXb#S_0ffY5k{mv(Gem;rw^GTeaPvZQ%Iepl9bLL^^&6$UtH!Xdx&GSpueKe3yJP2;mJj=V;{R^V5x$}vK&e;6B{MPoIXBx45n;YPiucsB<Qu~}c>#{qaxCT!7q10`PTX_wxxbumd;FNEru29^_yYJ~wTnDFoZOIz@J{=uY=Gh<c065Rrj%1el<%d48IpqhF6VRuJr$2E6+_~NbLo599iSvAGL3oAV{KWbE#QFTh`TY8=3FUtKNu2Lzu(EBr-~A%a@0VWr#Z}+)0AA}nl()R>cixEe^A;%oXPNJL2CsFVuP!h1d%Y0nua{uic(q^r{ed`te<04^ABgk!2jb?FEx!50d4K-?;LO9`AFQ(B_Vcp$L*o4XP%k}L;&;8oYkgjW*ZRB$ul0Ei&aanq-oMu8FU`ZQH<bS7UiG}}`wVgZea7MJ`wVgZeI}GWWwWZUx@bRdblXoaxVVwu-Sd5txDFm<`JvM`*H+n|U&PJuyp!tw4EFZ1+S^=<@#gc-Q-`z9Q)kZJ$B(IgJim|4^$vD^;ON)8{H~X{32tui=JS0Z&i8>h-v_5Z+XrVJwhzSlJ~*81gEJ@F2PdEHL$LM4b4sh*+ULK;`k)^Vgol;5x%njfre8jB$~W3&ocHv9WoxOMJAJ@I?Q1TmIVU|kpyuo`H1UFq2PfNH3rj0@=Nm)q-{V4&-h6EsxNheMHq8pU=P^3vm$^C3LtM`+_T+2fk5wN%E9|0&hqdzOof}<tbLvmr%!;|_cfG{<^%CdT>-1sQYh}&#%wvTQQTHXV`J9KF9WoWSHs57DL-Ek&#~yCz#YJk~>{f+-Jdhnx=-0>09#ZJ{yn!v5g?@8}w%qe@+Bf2SKSNvYd-HK$LLUyi<aZyfty?{u?mKaQ9s=9*i~P<raekhy9WljzuP@H&^+KG#zBqUC_oS%j(TZnhsP&E)%RD^s#3nUgr?AUzZmurcsm@V{`<_1LuqsR4*O#O0>&m%q^BIpaRlgBo>iY!e`tW<|b2pe%<2#ST**wI}q^xXppE|{OxVHS(HuX6CP>Cm>&F^qFzm?NeJ--&;+%rGtG=JdZSvF7m$97deyiu8(o9T~sdiDX_82;5Bm2ZqK_T-QJdybmVm<vAF?!WTHE^i+%r+JLMhkWND&gbEr_u+Fo`R+NRJ%7b6$m(;XqN%3I_@UNZn;GZ&6Sjo%ht&U1*onRWyFX#~>;3=!3Hx&~!(T<*h5iNpmWa>5q~3%7GuCfHE8%JF7W5|kUDQ@WKXcVoBBv7k7W&*nk9(+>{<?^A5oORKc*$>oNxcUDC#)TW9)g$p3B1(9@G`#wxfSRo{V5R_P$%^Wyws!cN6}0A6CzGx{Up|;zl^m)=n?qSBJ#oVQ6v2&teuCRfWIQ*s)!P3DSR>3g3uE9a_q?!=vDZOSo;)u1%9Q7_e89R{sI1d5gSC9(BHz-+DfPiZz5+U^ga0X==nZ$1AL^2K_bRMC&G^xF-b%}=wNtSi-h)r?}wa7=pguU=s6xb34X1JG!YrlbodWMtPrsdx(uGy)<W08uR!fGXqu~L8FH3^uSK79^hig&^uLF`3ta>MJFKmOz6<{WdaZ%3cGavw&KmGl=#zmS8LsD?AmTS720#t?7_9Y&4uF?AlaVJi%2i_^#{ln-K9kX7GU_K_eTs;&&}r~*iU^>G)L3|0i-OW~1W+3bo#LvAMNTYu6#7g<k7=lvekyVjpmFdsMZ}AE3mOYgYg3_b!N;RE7COaM6N?<0XDa%{p+_9*rJs(+bD@dw^F+)MF#{S8PixbmGvMc-HXa)1s)<Jq%{(1_644_O_0lgAktAX^bPoJNtj&VXhL<^uk+;~@Yc_P2YqnYFvlu-Vqh9*?c>Fdr1%9cBR1piHN$|8bAG!cO6}3sw#jctp<j~CX(I*8xQcy2_G9JGJO^08u*{|g#&{TL@ONK6ir}vFiXo{;Q6*)9>GWw*W2fc4d9}@9E#1m*W{Ffr0iKv1;gr~I-v<m(iY9B%$xN06E=OK6qeX7x;8uilO7V${L7tm_>`y!r-xC4C*PiwcKci^9*_A&I4tL8Cs9)sUTpKA1|M!ob|A~Hqvh4z8pBx0k8-q2p~n?-C9u?xBfeiyt2&4CXW5h0>I^cDDDiWny1HRy2omqm0D(E<8%_#q;GC1NOa6#T0qMr!iwrLCRe!{BvjC-{LPMxbs4YNX#MV!w!wpxfaOi1?$3ozNZd+o2ypcfjvM-hSu-_%R}07ttO13wWtL;idL~m-%lXS86o8ocGtbCaK+Ael#9S?dn>S+7a3nemCw>HuOXIy&^squ?@Nvem5THK=;BQ6Ok+84D>8~frxV=jzja{Y3&&FIQ%)(=0S5^HF?O%13!j7XVK#<>ZNZY0>45itpop@h#!ln2dxWV2dY8q!Z$%)Q|NQ>^+hxk(G2<%cp1-QU1|gP7m(8k+7P}0v_7;Ud^6-d4}AgtMG-AUw1&2YZzH0eh?k(P;9r7&5!w>IHEP>H+rj@pg#5pq=Fk@KKNayaP5#1WYh#yhfyXUSLu-xEuQ9mv(WC3sZC>yD{-x==A5+~h_dhuCO7E|c?#dF;%lV};dUON1r{adzRUcY6<hzLWAAb9b#{'

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
