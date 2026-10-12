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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_005.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_005.stl', 'source_sha256': '1442cf48fd16d1873135e18b8407f1e2418f07abb68647050cf00501f3bdcf26', 'input_faces': 134, 'input_vertices': 123, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.101352334022522, 2.7939722537994385, -0.6020022630691528], [1.82576584815979, 4.095099449157715, 0.32200053334236145]]}
GEOMETRY_BASE85 = 'c$}q}2~<_r6^1WEa6rTu5XXA;sh}b%Ad?7J5D`#(%!;Cy3W$mmGiu^9E{zylhr}+_CSDw3bX5{f8k1<`B@U>KiWci^pV1^ZQ?p_LMSIS_x2bluYjw4cwb%LYxA)s;pMB1|_dU#U4vuaLy?QBw2W`!0-A+-YwNu=b;_Upw8Pl>0eCEt6vr{^N%h&Vqo%ob-=81Mnv9i!JE4yG?zGsN)8JZL1>8*O^%*`*%&zv)LZhls_<fAk53bF++$jzLWEv~(W`ucgRe*L}G*VX^=)mD^Xm^S~dT8!HAeeE<k*7mW6i&1qe1y_Rd!IcwHdnLCig~Yc!qWCrGHIi%F>?x0B5V&qKRY-2V(cB=pI;Fo0@)WwBLY^Of0@uomDZaMo8_c`^9JtkPB=N$|Un2kdv&5r!5TDuVnB*3xg_P&MGq`2LwvUm&O%b?Wa*FukVJDF%DVE~9G&m#AAI_D_Yuk=+;)i0X&d*MsLH^{64^aP-D~PvVYTAPQ7mk7J5%tKgs@1hvZ`wEak<ZbJc&$xvCHfVy6I@-DhWy6CFa9j!^#Sw2jVb%6p8JXG!B1p>>%AXRpS^~kMgCgbUGV+}<^S5e4t37|7F<#9Q2h2=6mNF`+-R(%`1b~GmDiTaN^o0gJnB(D+*F4=CFAcPkLL!&Th;}=hxO{8-p0J&S5TeXf+~<V_vS6cx7tel?M1s}ypnXS9`jUfC!W`H0ruDD5V&&o0M%1-`j3eBXkAbHeiPi*=#F!!T%P_T=6S6KTs>8=6L~6&en9@yO~m(_=$z<PKg-eRX5RsMOl^-K@6xN_*58`IwOx$|vELur9w9!G>ai?Za|rcadkU_2t_D|%Ki`k|CH8*@&%I0QTGQ`1`dIA_u5Rp!{6<I_xb=()+>#nbyzx!sw{%Gdw=JAO^)DH^2l1P9aJ_0I;;lUz4k6Allj5&*rTu-Q<0+gc`&r;deK5t3`SA$qi_9b56hnPTbHL|I$zKVs&GG|RD)!;?tJkff_~rzv(=UPU1LyaHTQB%f-zxl$<NZCWsh;`?lt*uU5bG?sMSXY}PyIaUiSutXJ)}N#ilonD>D^lNd2%!5-|9_ux(A#<9i1OjAKU||o{#QQojZve$s;JfXy8%I7yE?f&4{A-*MkqE&fCO|>~U1*vS{kV!WOE3TQaRHZaLO#1U{vCJ58Z}9xpq9yhhhX)bCU01m5`cD)#+U5b;-c5WmppGWI1ulz5_JD{#AP8_v&n;ow$>K~(>d?O3n&xdyK652Sf5F1WubF(bjXW;#Dg^jNIda*MdtKAP4WpN{of%Ofb>c|66Z=3>1@*GQ@-HkH=feFxTSZ6I#7%Oqaa1M5{bEdy5{3<g)fD4~5xTTbyhoi|&e59-wFi7SRi@m*%4PV0)dXx<OU(7M!xv@iWvQ2ZV<#e0?0zI;hsYe)mv@7JJCOK~~Po5^){XhEHptW}hMF72<{Z~kH2r`o;?uIDVlzUbYSUcl$;=Z)Y-jW6~^Y1w=o`*`DhiZ?~j=X%tEWjME2x6r&HLulSri%(#GJME(S`)1Pp{{xq^nD>*z6yJRq^?%OC_`K+kYlwSKrFA*mSEKGXPJ-L^y3jtR?LLk5KYc{`okOW_v!<cXhTcT$-Iz}Gv}&PqyV|1(@$E)Yp6ESvPHH<7??LC>NIi)@+X77BTH093zvS>?>L+pAl^pa<`E=4>aKF0kP4RY<&^LX<+V8-7#ey66JSfj@6Q1vu9k~>59!33Bw?w0FvkR#n5BgrAmzk+=3wBfd`+X_T#kGGz-nt9mYWsB5WBmSR9rn@bCe7<whI+Iiy>Eb@z6WldP5n2tAnIF81H}(Wp>un41^Q;Ib8JTbTDos&=VwwMp8A3-5h?VXD%@Fs{6oUPEs=$&-#Vk}49>~D7;sHp?+QM1GM>L$#TIZ|$YduvKM|<kmQh7{>{e3!8zWJ_^6V>c>$)K1(Kb)O_XKO#+u*vnfS!-TT7HK-#!nPqIGvsgiGjGU+P-&sjQsw`sh-v6aITcNe&Dvtb?uSo`X%}v@*wXqozK~*Q`MK%(f*c#Yd)*!^Rn(C?YrwDaCPM-+TTePyD)F_n-qU%Eb1}pdVY((B~?=X;1bkhJeiK~OX@q9D9^Lw^c-x{XCLwhTqCY|B9Cq2m7}<SW<McrYNqFMH?ObJf9F0=z=yw$`fb1Y;2h4?v;p9jmEAF~<>>45J#FnEaDD1x>c3MU)}<?-fg6RNP@bdZ=dmw$4}jawWzqdS(S-Ykb*Wnm^4+>l_nEJrT|}Lporw<!r@qy1`zv^A0JzPiBk^M=u2h>}`W5l+TX9jxoP<YM8}Tb5C-a4$5E9~TJpTKi5HtM$yPpt#{{Qb!2(zeRg0OgDW*$c}n<OlObprb&n<6ZUbrSogp!bTB!a9Y0l1&ws%sQEULxc?#Hh{Gpy@mM+^B2~iwH*8LDETnfavaDebpUHQ4ie_e@9)Q2j$S;c?+e<C=ay@T;I$|47|&~nWM2}G3A~0;>`UP>iM3o~6zeFC8_hbIwHy<LMf3G@EywXZznp70YdMB6lXHc#4rN~?&ohGc2=<NQdBa$Tu`ir;6zeFiL*wh`dNkJ+!t)GeJ(TxtIM3tD+LwKyJdYo1KlY8_dHq@Yvu_ydFxFvQM*v?x*Wp~(d|~;*7O<9M8MAr9N?Dh(PqNv<idh%4PqOL43RoAgPqIv5vslk!pJWq-WwFj;Uz{)>VX3U;IGI^rVKJ;@*e6*pVL_~e*e97PERb~|`y}fvESPmL`y}%e7Rx%8eUc3pmc}}beUgn6mccrMeUhaM%VwR;KFNM9ERS^_`y|U1R>Zo9eUi-)R>Hc3eRFu9%2=1N&m?S&u(3SK>tC^!V;?rDdkV`DHbdAn9_95+)^eQ7CUqh2!9?DZiF_^htedc|!n(7TV-IGXg>_-wg?*BB66V3$gME^96z0a-jeU}J5Z0b`d-h2t|9jMybzAmH)>@bYYX|m8CLa}ctnJt**((aY_)!9%WUYkRv$kiSWNm~wvUX&jWG=#-Sv#{&vR8$<vUX*kWUmQxXYI~DbDW*Mo5O$lSK2>c7Fpy=|5*FicfS1ieDR&5MWSCGrslX;ux@+tCl6MPtV;O@f|wRc'

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
