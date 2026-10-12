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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_004.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_004.stl', 'source_sha256': '39039b591677f3c04b0618368b19c988be9ff95e2c80e40c1ca5a369ac0bce37', 'input_faces': 160, 'input_vertices': 171, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3026430010795593, 0.18364742398262024, -0.29832151532173157], [0.33973556756973267, 0.32659876346588135, 0.2741560637950897]]}
GEOMETRY_BASE85 = 'c$}q~2~<?q8OI-p6;}x0F7U(!ttg<lA?g!%2?%i)frkQ$3m{uG5Ph1eBp5X!DphebE={CrU13ysfb5Il(l$}kF)2}FLOhKcdup`v?)M+^uE(C!)6O~f{D1TF&Nufh_nTo14rpcLB+#R`5aQWfl3_0h+UOuS38~SE$+1hKlZM14thEyCnb#hc%nF(l7`(trNEOoDqoR|RB)a>G?tU?&+&x71nE1rx#K^da_{6Aa%}<G3nG|jINy{P=qRr0-c#rh<5Qh!)5Z@R7$45K!5>zGp#&|8yeZ^9-OKD`!y&~9iL%c&B^MhVoFEXe2_vJL-I+vxC9n9vp_-XxbvezBi!o0L=1=aPN!0H&(PB*kV%A}PvztN{wOZnW_tiBY!oq0Lj$mWY@yWY@y#juE8cV#%$hZnD<viCKWWzzZ!cQ9`{b*Y9u@A@OFZ>p=Hb)U7VXX$pE-gjLk^FreVR!6E^NyoL=j*h2f49y=~Md!id+n&6}UiTv6g5FC>4a}RA<LC5V4ZX`!`Ed-b-@%@I#v!&&Q*Jh`2VVGTR4uMYgWgNl3CtT7&Az7hh8f$KSE4fO_1-ksNOiidsndJ0?Z22e{p?z+_e#nDcK(Gwxz%v%DGp)Y)VobJ=Y3BwuRh&a$@!Z5RA<Yxa=ll5+OhK~9JlAZ5aG$Zdaqj<cf7;bGq3EhFXh&M^dj?OzwO1`e7|<={44wJ6>`TFFoCX%o$Y1reb3BiULI9%EMj{!oaS%LWY<O7mUUh4)$iTtJU4_j=)Le_0iDl%A=mU?p0tL}|EC%C-2ALO=B3)8I=wepH!&}abgt#*pR(ijW6OH3Inw!$>run`v~hI3TwYY^y)-9>ymv|^SO42v%uA&Y%Jtqb^EtimL>tZv?>W=HSl6M9J8zXC%$ovhxOEDTSJ3>yHl>_bk1}s4-dL>n;=JcHKf9)os~_V@*DLeqOI)40Da@;9uW;8<h{|DJ8WVPbyDqDYbf3IBbdEc3=!b@&M7B>`-uLCVbUucRratpa9?h@Fr9RWVi}vryKfbYVSiExL4p&Fm`GlS)oTv5XEu;S9|CFxRYyC<I@wmm#?`!={u^P<08XQJ_G|Y$9v3S9i`lS41GrjK_@~`(>wI-P6zcrNW&lYd#^YV?2bRN<|n3wL1XLV$I>hl(F`Mi*C2GV-|7Iy1R_p`-Y&cD>0K=ZH0GjHj)@}pNpMLI9`dQ5#d#gFrfvu6W)UAKQ+(R-ou2h2+&?yH<HBQJFP<r3#zj*w5=#LZXaJm%%9cHDgRc@@>)yU?ijhP$_EJvl1BPKO`JhkaO}_wtOk?D$P__wqSEv_IV+%4p6@w>-&jtKp7UNtoYA^}e{wtusHBK8Lyw<h<gRL)Z1-LhiVvh3A<!oIb-Hm+XI?>R8z_uijiu^@l!W_pRKwN3q^Z%lok76*spoVf$iu61{J7I?eaKRIK+>moM4%6|;`9`EnEHTaBjAkw6#DtF89Zeh;!`eMZerraB2*=zB<t8}GBeqkfgz;i~3MlT)bvM*{7O@0&{XUaen>{?^FmD|6qa{pk8b1$$k3T)o~)kNa1$*Y)krdDV73^P;@Fj;o{IBLBjP^Qu>;Dz<)`;#$2I3UZkjKYLW8_l5$;YWBKO<2WxFGsq9vS<ThIpU=GL=U>6i@7<a88M#@l(tD+OBJ<+n#B#1q(;oWV{Oij~uFe1h^M>?CWn7)(cC62c&67AUc!>15x!#AXWBJ^aCokdFDb(3g|9SN#w;nlfE%h1uVa$ta4xQ&e-=Y4W>#FL#nruh=x;(8&??s=f<d=IF>b-Pw1?~5bE4Vt!#jSLoUytVN58B7P67F|d?}ds|nm=tr(VM)f$Bau{eY>xzZ#>K~a`V^P(0)HvS-{PY>qh(3Z|fCqJ*P$5*Q&_P7jnjuZ(Nhl`F0b?KhNRUe>j}_b;Uz&ox<e})W-sQa^CdQ0a{N)61RTSZ6mjSN!&;0S?*5PYw(z2y;o+nr}KZeiTX?fdBHQ5zE3_KTf+IndGvk5_YOB-84*jLFGnBn^QWJn{`1{t^2&blvkKXMS8oK>>%Cg?jCoVqKkM{fx*f#!wR|y^^M(T#>ArRGFXie)8)==Z9#Q}CIzaFH<QS_X&3am^_fo5`sLzBR;=GXWMc>1-TVK_ClQe?rPdd%KbdS6tGmiBW!BAbJ_tMsHsQ-96GcSLVOWtE1>l=#e>T11Lv%aBz(sZy&@5Rm!tM&W0rOx~q`a7upZYAf_Q>dS;$ST)+!<+`{Oa0n&UdU}`UP*Q2>IlOp(D(D*QDu6sv`(Y`gTB`?fBav_KP%wsD=yRMdvY5G<_&w!(Q!>5N8hXVBouJoJCyGK<CXb(uY@Y(Gx``gpS7Pp$G=#^>ZnuC(|IV_!0s!<gZ}k;uX-EF?`WjI?|ciX@4XYj?<0%%P5*Vj2Xnt-ymZW+EZCaSJlYCQLQJIYCk*xvg3yw0{s|-2=fC?2V}#fL`xC|r^BR6{9;=Z1!K=XW$OGVba02omH~}1q+y#yVM<92ABfw$E55ZyJP~=D8Q1Ale7VrY_RAdTxDtH<)6+8_*9r-SJIyeCN9ykCTh)f3uf`gFngM+}q$aUaga0pTXhk)O~(0Bv#Q}71x5#(p!BjC@GN5P+ik0CdKkAXLv$9&{G<R<Vu@Lc5Yz;nTKkRO2OfM+8&f@gzgA=iUvfoCGqz%#*bBiDl82G2mQ0nY$0L}q{&f)^pTf)|0qk(uCdu#Ef!EQ1##v%!nO$;iXtWN;Gl5I6~(h%|r`!K;zE;ML$b<UVj5cqK9iyb`<|xfi?~9E;oojs-76?glRdFGXg7mx5!EJHavFXykTqG&l;m4IBktf}!!p$UlI!JPsab9+S*t1ab;kOMh@1q&0@dmWRfzFf>L#X51b_V>=9uM`CE~i=put42{Pl{lTLIt>p`XJJKH9);wB+wX_0jX#>{sH(>3z<PKmhhk&&l4c5{RJQg_tL*vO98c#$@;J3`f%{&~CeZUT2M`T~HBiISq59|c)jO-8Y4DNy)0PX_riW~^;3hsvdEw~%FJ8}@XJGckZ1Kb1L6FC^%6Wj~w3GM}UMtXsr!7fN|unX7~ITY*)7LmiiBDf>c2iy_d2{{}b9AIVb)apO|7s#&<MZ0mh{}6fomHgKZ{VU7OwOYP}1P8R%?m6>@v1ZN2N;|W{zX7*?CQA'

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
