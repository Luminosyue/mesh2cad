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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_003.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_003.stl', 'source_sha256': '914c8107652b4b6190f39ea4da12195dc99605e80acba4a118695187dfd27143', 'input_faces': 392, 'input_vertices': 225, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04068147763609886, -0.152170792222023, -0.366612046957016], [0.045668356120586395, -0.054356396198272705, 0.2869548499584198]]}
GEOMETRY_BASE85 = 'c$}r033L=i8poSU4hcpCK@2bfGzb9=gi|EVA@>mw44}YZI07P)g9HL0orI7;G=u<hXka)*FoBSZa8D-)aws6DEG~}gvI=ik(OsXcF0k``{jZ_A$iBC4cX;3X|MH)j>guYmtE%e}KD0*7Mw;~r)GD7%$XM4{(<tg|jkNe_F>x~^r^R-hGj~BX&7Xbx2wgQ|?C|jM)wFnRVbIiRv5_%BJsm;4rgsktb_7j-J0>n>%ACn>$4s3@{(vd7W2brj*r+LUr+NQw+o@BRU`OZYf*nbY|M64L+XPSNi`(4PmSwvRk?M6<?;`d5ql|r{TF1Slj{EBh`0uo2_Vs}w`$?T?gLiZJ_yv~Vb1;`Tmd(m1HMcb1%37<ejO)33kIU<yblbw^k~2&A`qj2s<ri((%zv*u=jQs$Zu51`#y_}N6LX6B`=Of(`TK7#v9CAG+sA%+X>k~7uREK#{DCnC`TLJ|+k9=-jWXFcZ(p!{+?Qv;(RA`1>$-2`b~=u7J+6WIcK=qMb-%f1E&t3f8@S%FCl2%VYi}%;edBC2->(7RES<le%f~l9!v433>9Vgi9bU@)hWcI2Utr(as%-_gry!d9NBG*O{(HE5r&ZiPTHBO0+>YdOzF$wm#PeaYKYxF*>^t(itm5`eJ;?p9k6uzN`-Zu=i0g&#nb9(r{b7Hz$|ny=mwnA0YmJw)oPFbPKo0+%IibSxzrMun`0m^a*>`vfFLQlkqS!Z<#&Y|OjRVev$^PmdC9<zo+|TCvI*i_DyI<kY2;5`4-_{4SxIgF2s+8L!d}H$vQ}&%x7iG!q^t@2>3itmzqpk9((<|ln`}}uDn6mF&+hiHn<M#{KWBe<iK=zHBR^B`RnZV=dh|bC2>!tUvl&>p%=kmFx?3<w%mvTK{-Qj+7rOrGaCi&X!S4w4Hi(kXO`D+E2cLx4?!7ckcT9(SbE6ZSCuRFP1?tkH%{v$X~oba9Bg`~^<=Dg62+o`v^lg91Nz_?%UbDs6faQ3y6c~<=e-<O9;zJ4!suk4%szfWcV@F6Qt4(EK~mVB+l_)^(7CS0)myKc@C=bpf&Hb3qszOFvE*pz*vo^`)2rMzk6?3K&wDQB$q^iHz!$1jqf7vXC=!Z;7j)_*TzzfQ1K{%XTYTmQf}yKXUM-_xcbh3om|T`RAeHM8c8mI3UWk##EN{uI6^zreKl4Z0duJ=4o=c>>?Ob)#7J^`7<FH!9ne%lRODy-#VeEq{XI7jr$1kfVJ4$<}iueB*j;xBPtRJMScM`~K3N%WGmDfN#9g&@Del=DnSZY<ZP1;fggbuPtO<a%G>KCqBR5?^Zs;ch)IQWZ(6}UO7*MZw?MBk$q3+<yLvmPrP2}$Oqx;5v}*j`QY<|I&l3SrM!_hsZ1{K@Y}zD{ZD@6aWuvA4qscl+$}%vo~T*#`TL)*+4@2FT8pcu?3?oz$FY8M)>`i{9|~U!?z>C&jl{HAE}yjCmY>4cbDy^5r{i*H4ExEMwmcNRGbh-VhuZO#v$?+Ni>&by^SSVwhVb(u<`cdB@R{uU_pFrf%je%uwB4^~;G2>B{q~;w<b3w|M;me88t|RDP1x6N{cg*1;hTGJ6xs4T@7^T-{mrcXa=!We>jP~0rVWj-{2f~la6cd)gm0#tx8;woe3YwP&O_mAcau1Ov?6;wT5MryRrQ!D^NQtqjF>LNs9lb+iMHod_@2|Tw&zj!Mq0<Ca()Wmb?u}*PeeUodu{n3e5c>*ws91`@43#6x7S~NyjfLwW7A!CRrMQDm)%vhM|;Z8_8j@jXQuLg%%R+`7C(=DF<%K^KX==<J__GF)uU8?j$C@<2(Blv7vHbzXf<p92H*6n<ohzqZZ46_>(Qmwy3+flVw;css@}En9$P)f=kKekys_BYHyZ<&71`Re;Ue$9b?h7Uoj=bGt0F&zujZ%l)jah1N*+2#4|prAihLHnnxD?!*IVV4=ga3S&zJek`nh~v<@pu9`usY7t7KoDAAG(tKREtc63f?B<{zK0%s)ntSLd;>%x^wlncrN&eHZX`mHAWn>ip?Bmy^i%rOeO5e`tRGENdZ`SLT1=tMk9^PDtkOmGwpV53MgDkp|zFvVI9)UB4X1PFv-b^;G!kdg}9)_0(67vYr}+9?MtOcj2q+yD=^_h0Ck^2jMIG2Xogo_SJoe=YDD`_nWex5&lE_nIjeKtNSJ4tNSJAjodW$mHn9TAKH%{IK;lX-xI#N-}9W>!t;>2pA^2jpEOE}c^|6oV}-BoV_mf-EamGf`*5GH?8Akx?!$$z?!!Gl&S77DFA%=^UZAI4v3%vdL-^`@hx5|n4DJWz{l$4}Qzn<k{@-kVo9A2Mi~YZrJl&dybN6N1@<%+sU28ArdX)Dp;j8aij=%uRSKi}%zVaTYc_y&0z9$M_eNS`-G|A%YEAOGgSKmXm7q4b>{mOf>&sW}yP3<Q8>U**9)%RlKu^KDne)G*Ie-38<q4#?D>U+JTYrmD;Kgzj*&sWY3%;W_2)pH4-ubfL5C-Yaz?G*Rxc*0}zMSDDxTfE2Pj&m5zzku^Z_~IPK?D4XdKS}-9TGzLq^Z0z_oX2^-=?ARJIg;?jIg)eav)s>~)a!ZN9&xS}m|(RBzBt#?I)qv8v-9U}=Ii48&HU3in=j7a%;g=e_P;b_3xAJuJRS9DR~l?(Rn7y2FU|w?1#Ui9bYu_O&gGT!OyP@jNY8JnT;9Ag<s-hX*hjT*x!WCXJJroDY?<z9=>3T|>S~R&=~JX5T{8J`fmVH_J2UjZI@0ajqtpL;r2CY&4Uc={F$8fvs2{i<xDNDDa2;@6Xnk;9a0946xB>V{XjAZ$;2zMIz&*f=5X1`+#EA&vXP`~N&wv|3{lN{vk3j2#9|3F7N3{nZ;_6U8aCLA^=;L70+F-*QN#1xCLHq<F3FT^oYa)`Q`jezKBuVW|lI|r*y5A(JPl%5rh%X_Czd{gSM-Y1u#9t$b|A-*Ij3E9LYJkssW3e~BL=gW0L3|BCd=)`_1ws4;f_OiISmXe)$PHqVKg1%(h(#U}i(DlZ`AjTwp128uxF>=*89{sidLCTE8@0Sq%^Tgk(a9Slp+mqU!BNnu;3#k!G!sm^1)K)XgO-Eyz{SwL;9~F|1o37B@y7^a6Iu>7!4=Rg;0ka)G!vW;eg{G9giZxJ!F`}Zz<t2&pq;?&z|SFwL!jNjA>b|u;;snd?$D9o?%;4}6gV6_6PgB|30{IA-U!VDZv>Y>i@_z}BIq7)5%>cH@%zxt;1p;EbTc>uoCW<DoCRKiAU*^&!H2+~Lo2|agU>+o!DqmSq3?hXgL9xxa1Qu&1aU`bA8<!-b7(tob8rCkIdA~D1A<tGhJbbOU}zWcVDNAR@d#*F@Cfiw1aW6*cW`HLC^Q@#3LXZX2_6QX1ziH31zw6Ec0o6SUEnfk3AhYg3M~Scf;T}w0B-`PBZyO>?}J62r6P!@BZ#LVh$EpHVA3pbBzQ7(1$Z*}HE)cCu7R!qlO6)E0iT9`4n7UO06hb~0KN!44892d44MP}4E!GSb?|%OR}sW5p&h|3!HuEK!HvO<paI}U;1<vh;1=Mqhz{rvQXTvncrtXb)SrXV-=xE({vR%l*Kmv>=?G~|iDy8Ef@grIAc*@yJA?az+e1Ua?ZLs&Vc=kJKj<uQKkysSrQkQf%Mrvop)T-Fup3$ic7u;VOTkCLJD{7uJHX4J>ELBx(GTh98`4y8D*BQ5d2h7xMlWbvFzIM;FYq`7aU66Wm~;a;4!jzA6ucT-2t5HV1RwOqZfGU+1o#u^S?CGy3Dk8KL3|9l0elSnA#@)2LvTETcp!8%cp$h9v@N(T`l}6s_-Svnh6X`ffm@-kgAl|odgB%7An5bpLEtgaUf?m{NzifNN#Gc095@dB9)lpxh8BXe!Rw$0!Rx?VrLozHAYSW@ccH7GyTPl#>!Fq4_26yNxNbubZ$}WHgq{VT1fN3?pMo9(AH%qwLJ)t1AWneBgX1yA2?*ks5yXMeHsCfG*FXeuGX$|idyogj{h<S(t-%Apqo6@x(ig#_z!BPmT!}ysPec$$LkEFL$AC#Efk|V)q}kwXjCVA2D|jo$HCh_)Xaw<G1o0f`D)1ceThR63x4^TZ+rYEIZ$h_&-vqynAYKVQ30?^<fSv;vfcGJYcR^2qNk0Pb0_Q>#z`5X9=*!?(@C0Zecmg;K+6){9egQ$;8|nb}29MVs<j{CTf2kk(Oa0Ry{YN?gOgc*H+fnFy(g<lRBBb$(z<82Q1W&|x6VtlCKzpz^AQt-vVzI{{7W)ulu|FXedl+J|&mk6jA!4y#A{Kip;<3;cU|R3yYY)~$VzF)#i?x+ltiQx!jV2arH?dgXiNzj(SnLysX&(_jv|9B>HU86od3^9O=q1|rA0X9V+K<)bUtads<vU~xA6kpfNVMwSe>50B(F&yf8wf{WwE'

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
