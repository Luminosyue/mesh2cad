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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_004.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_004.stl', 'source_sha256': '5a71868edaa03b3988e551973dd9a7169da3f106af12bf4fe5d6498efa2a2e7a', 'input_faces': 320, 'input_vertices': 199, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10910516232252121, -0.04246076941490173, -0.014088393189013004], [0.19925463199615479, 0.016067028045654297, 0.19893373548984528]]}
GEOMETRY_BASE85 = 'c$}r04Nz5O8pmJ7!mj`qc2`%kt7+g$2uUhsandpoH4;p-)QfzHkY4#pMeV2v3Z@7uh^SWu!AJs=Qc<}A*U)XZwq3W`Qit8XoXuKuo5pr)XV3FK|8qI_%xPw4mzih&zw_h0=e}R(oO>DKVtx7q3H})&Ua#&qIwVjCs(~U%<fUZgq$j0hhb?!k?j-`Gryo7bXV0A#_k1srC-Q@nQ?iq?f*-L3Pfnc_9BK<rU6GZOmAHKIimc=m^3xJCvr{ymy)@C0q8*1sL`8+##*YcLt+V})KmD~XbjN+&8cltP8@7s4`R)h5HZ5(o(6iEq56hE&b9A1Sw|~)`OWD2gDfaJ2Y>+<SM|mFmoK5U+g{acwJZ7)x=Q(|qeL%E>()IC*f;J0pyJt*+%)l?%t5fCsIx{=6rN24;9QP+@jXW>TWA*~)u@5g{Upji7eBVzOZj`TE_6d9Cn}xF7l-lAp3-6kqRxICl|0CylT+J(u?akiP{%k({C^>%Hhkje+>&k|-NiRO1Mz0t4kG8d0c<0XYZF1b54)|o*9~;`6y{fm5-NW8qm?n?^<tO{&x*F`_`OH`*`;Gpay@=udi@bRDLQE&GpuO35W4!81^WoP|k>kX8UF{9*OYh{$abms9Ud4Ke7e8e0+MFgm+MB%{?Uju_7o>My$(Q{s;C*QJ_8Ytp#j=s?9bc@I=Y5H<3w7u?_Ho-+%Jw*q*(>^ad}gx`aAwQ-EW&x5e{7fjys}Hq&s*^qWj}rY$^M}|WnTVV{|@PIj@~WjrP$`S^0rS3-;sV)IQ!)Ma<BF#?`eNuE&IRKSIGVs4(+t^-9t;dq%XY8e#yUgd$l)tPy5eH<nP5E$3FSK1D1DKdDoJtOL9L9KEb}RZLhJt+3W3<ia~OG;>6SYjq|3q4r4zhM|$O+AWPr9tBmKlA%uM&pK7o9e{VedUE`{a=P`TzJZk5o>~DWB&o9nicU$@H<}TS@)WoxYvZdPC-t6`Eu1y*2XSW@Y`|0Kxx0P2m+~oEZ8`(S8?DuMK@_KvqqiXhD*AB{g?&N)A_O@ermw3Kv*k653dJ)m+w(_pY-}CwR)v{k-bI@zO+M3wMHI^H_7~IM}EcJlb`Ayz){!ic^|BF12`b40mciPK&9iM1tuZ%xn9Ix5y<5f<5%>Ln6r*S^bUY}2;;41rDsq%VPM_qGUc_rpD_w(J`?9V=X(0G2c_pH~;19+bPdfe%?-%MWLKkC$h?5Bsy>(svWl-tU?27k@%OGdIU8Q^_>llPo|=2-S;ZaKZKJCpZZFOCW9d;1>py6)^#*eA{QI*-|VuHPL`v5y?SNBZA3xUIbQz~lEVn8m&!+3B?p{nxW^?^oe9KPIowkMKFpc|7E>+$XqSnZ16$QmY!-uenlT+z)22?+4{lGy6$N@^g+$zb=kl;#4c-=P28N%Wf;LF1g0%S@ApeVJ}n~uM4x+uM1cD2kfKb4jIQ~_MZE2`JdUJFRC=or_2BE>|KMm8vC!b`pV~z=sQb(4sd37xvjhscAeMdQ$O~iWvv`<z+AVLw=bL{k6qu*WFHVv$m=l2ZRNYajpyf}ErEU4Yuk<ebXBLb-*V?wnXmG7ZuZXZ-|)ER=dpKuBR>bIfxd1lFBUlY_;NXCLcbch?s%S>z5YCP#n!UF<10VUxtem_R=)de1dnS%3;KCTey+7Q^>JHy+quK?SpDHNd;iEI#{QVS=lMS4UH0ACrC$3p{bTl%BBdAZAKg~oS$~Y@?Xz3#?RPTdanzTcR$g7&%Ex^~7q9z3xv!i`gxkt@hw{9;67Obz!)J$_hXpNeE3X9J=5-$%#{Lg8YUMu1=P0w+KSzlj;q2{^@_U5sPd7TPyuIQ)ugizi*oS;2*USE1f!oU44vggf|9%GhF1z<UzcYvZw+hea)-je|e7cV3c~JuU?YT9^ahbhmTrtV)GtSj|UDq$Cv9EuR=kx16*8a^yeEl9>#{N|4W;w3JA#N+L4&2WBFe?M=IBdQg7p^0-x8XWcXBM%a-YKu&ZojYGR^GMf4EHC$nEmJ*HO6r%lgrs}aq#z+S=nwYFKm&#E?+dT50B0@USDRfUth{A$JsZP@qJ^+XKpJm656>xIW6of3%u@2;`0wM54(cpb&C6;*{ir8db~Yhn{j^3UY{Qka|Qh$xzX$TGI`JSb>%v)qkj|`_p{l1_VbzB=x0oc*Zwhk>>p)fU;ey#YEQ9opPRkD&s}zZ_5t&Xjq|1i2eG$xX3E5K!R+<tf@{QJ_R2>Ia-Q*=HG8N2oQ=H?=eZ{Lvwoj3d;LD6^a^J$CcWUb4|T83Trb}b_j$9|@AEGISoSwE_<J($w`Q;3Z`H5`?CtL-$#!`Dn!R0r{_4K;<|eOwxHc2*Gx+Z+cs`oF=lSTD1%JpMZ5Xe3a0C19yH|V8ALsQ~w*H@8FI4^MqnHr=M36{LH2jH;q?{I{^`F?%Bmb*Ev5kKy{QvzETa?y^V6Db#MI4FaF<MQe;UXUekJIWgw0{h*8H?Xhn+Rky_zA71;&oH;nsNAjEZPu1jpJE(O%ix2j$_d#6ZtGSU#obukH>40@cRvDLp%@1&*L@Q!0|Yy-|t2n;umpDRe|=zP8?IdYT!LMrd(^_jW}KlPDZ{2rkrBnnK+&T4o5x&4hM%K!@!gw2L3gUDMuUl0USSob=G+dj`g)4i+m8Qukko!1bCcbog=VL`g$c9I1|T7hIPxteCH##8F)926|EL)^&GMY{2X`<idaSN0IT4wDB^uu9Y@w6cYtfa`;kT9BE0v06!8+R<{+md7lRk0-^44mTA@`sia1THEUlJmm4hO7Ak)BUXzxG~zl<WzL#_npfmfl3b5X?E$aHWVat1OTJOexpnFgK)jzKO3$AF(fW`U!TbCFr#x!~0(;#ZJ4;8(y~P{iwy4zL4ru?|ICj3O>T=79^qn~<x(o4}j3DnYJCt^%*ZJQ8n3s>oc?v)_o<AhW^xT<d$4nD(!NoQ#YEPX<py&HzsWPe4usPXJFu#(*b+A4NU`*4KuZ?v0DIN<<cd6T#Ie;v>lI;3MGIQN&ePuPUrz6}-Nt#H*2o;6l8&z8{F^qK}kMBNu@eq2I(Vt=w9@jcf%kLoP?Qf|r9ckf*>I;8YaxF%<DzDB=sqR&Xoc`vQu%6GeOx=>lH_cc6${P{j4fx54^&>QTfgDB>4U#CGIzupPV*nE_r1o{vlg&j-&z5ida=11|yV_e0_u<XfWWUP^o%MSKo<0ek^-bPh#)21VS4ya;Xsw<9~i?cnoTokpHTc7QuDzr?R2k04t_&weJZM%IJtG1vOFKup)iv&ebK6mSaGV;;uxhGC3vU_K}h8|H_2A95#nA6UQNP?jKfg6UpYDthjL#9NSuM9=+`xXLj8(<tIbWEHpy?Hf_Vuc3%*k)_~T@Bw5o_yD*PSpcpCmm@cU%fV&H&EPWdF41$3-i0FGi`)s`3qFWE3_b`xihKin6x@J318x8}Biq2u;5U)&;5Wf1k>|lD!6!t|9zB5~ZbCMK8!^{SDB?O~Ew~o*TZgO!S7ILPkY(U9%vT+9FL*EJr4D%%d=%raLpFn(G0r;VN$^RGhnPN7KPC9H_$=^L6!Bvy;wThxB#L-Eiuhp^@gpeW$5F&jqKIdsh!ar63sA%_popJG#)F$M4jK=AO}j@c`g-?Et%hjzGh`4r2yKY{1pR9Teeq*QulGgv2m6A1BkuzD1`DK*==mY;h3o_F1-={E58MxZAResMFSH7Tqy7y-27&|8W)Q|j;~b701|AN+A87;M4<3aa0UiY&iM$Uy5_~V-llnIlc`x{0v?2bLRzF9-hJb^R0pI}4ug(K-><{jb><jJ>ra6v_?bSQT=coQfrsqec$@cn(8S^W>zxEqnnW~-3^GATV*t=+5w8ic%Ka7u{85I8k#Z5eJ'

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
