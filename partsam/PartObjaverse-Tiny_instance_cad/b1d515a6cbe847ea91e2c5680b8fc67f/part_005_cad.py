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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_005.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_005.stl', 'source_sha256': 'ee4d4fca7b7d58a77e0c7e2b2f22b262bfe3cfc86c2ded8c27349f4b91701f40', 'input_faces': 198, 'input_vertices': 166, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.2156786918640137, 0.023069415241479874, -1.0182421207427979], [1.1976227760314941, 7.414896011352539, 0.7346189022064209]]}
GEOMETRY_BASE85 = 'c$}qK2UJ#9625>HD}o*MX$(cthy?{vehn5x4R(ndehZ2PMNky$Q&(d&Vz0#b6x1jZOGM3T^esXpAQlic*nUgI-lI9Xk-hhuVVC6Wp0j6{bG|ckzc+X8+?l!eJ%2-j9ZI<f`fDi0PW)tf)v7`$R1_{EHavRD*pcBe%_m01*@>#))nBn(-FrZ<kWf1jD`vWn3Xd5X?e3?!`;Ttt?xnepo)kSLdicb!NztRi72kFEgqU#2$3zT|3YTLKZyz5ot(B*jHe352{~Toq`uLcaC#2Nc?Y$fzrPU?$kQ(dpwO=S{&3lxoc>U)Ln;M&X@N?L&cYdUJvHf|f8rw>peFppPGw&&0JDz$S_KU-w!alR*YuHbU`a+E@`3;D73juHTIDA=+#eiXtu>O}P%UKlPt$P~g{dE4J;*IPT@8SOgaR~E<odvIj#1*Nr#jo;Dh+`n}BC1kl_(>V~S3ECcg0}^(g@4^Cu>kz4rw<U9r4H=1J&nO@{)P9!uefigc+q|GDcHBa2Hp^tQ`FcNx|iZeJ4^g;6YXKY>H0>@Uw#_A-qx|S1#xb<sOA|-N5E?iQ^6a#?M&2R$bRBmAGBe;-;8|7sRr?-PdZ><<s5U7pJ$_J-Epavu<neU46GYLyyfi9s<2P%e*pU`>_hga0!tyDAw~O<&z3>pMWZHnQFrHpd$gb9kTxTY@^-=VApDM54c@Y44(g~!wEqS3Bf`P!6_T*7Wy5cm;QvGrc=O%#Cy3*^mWTbmxK)UCP6xnV*mcQ99d8~6uiJ6|oIM76%amX5!hZEf0{-)77hqk-z2MEHx4*-G*OO#_#t*!9;|TIBUYt&X-*3Fg&qfRNTYk<h#Pc=}`!E`gK%Q;>epj)+ae(-B2az|e=CT{u_tw?m^~o<#cfEOV7RFgiDIe)6uoo2^aK5yIab$le9(|?zv_L;tv(oP%&yBXCj+*Z##AEC^d<**u>w^5~4wY|$cPo1n`CmL4{h>dNKacf_hTXtAch^<KzH(zIo?(B-xir%HW4|J+%0BqLXVQ6{REYi;r&_>|J}MTx@Jp`(KTGH4!LLW|Rn%vRLHYdqz73dv{QE2LA5D3)bV|R1{0|NXZ}#4WJm~q3Sl4({3%p)nfH&&-px;fG5d~DQHOP+^`!Vh(^W0wC6Xuha?`i-2ux~9p9=s*{YFWg&e+%-ajr<`W_GtsqCx+iex@We<UO=ARg3wpi&iNN0&qjjR`yEE!w5oOC$K2mF7yOB2>hpu`Q722-b>zw1GVd|=X+I0`*oMra{N;7SJtAJ_LE0{v=a4s#49ZV(IM%gzd<EXNtPt_biw@`1T4fD*?etaT$6OhNb7XuM1zzkMO8KvS4)>wf!j1fx3BO?7?{CogOkZ;b_K6YHhriC<gXcp=g15}yvL55GB;3CudJyq1%nGR2x8A6iu(l!ohl%J1>(Vszq4nib^q1)Ai~g|;cykhVt)_#w71_aFq^>`W{k&>V_9-W5zn89{zQ$)m(_kO<9`zO4gOkYj=!z!t)~YP^^PL5Bf4=$V81g)B7uGe(TtA0+x_1O`v}}iU_1d#@P{#}3;odSTG(bP-?Z;;#j!SEk;Xm)33-|{eDSvwMcKCnpUIXjyC<1TU6tD&MYpgYq2cK_oUup$+H^YCxm|E~tG_MfrmjC4|?CaHrdhk=lna=a<%4^~O$ClvrTEC;OL{<&FCxs=3`mJeZD)trSVWmE7;|lxe;q+b%n!EvaM{RWwPwgj9Fu&FE9pJks)<#{9^ms<~8<vc?-n_;8TD&gW4e8T?-e<e0&$ar4ab9%SZs0{u6YNX8c?tjK&BP<{({XnO^?6U~s|yW}V%=RAkT3n_V%$ffQa0XiM#7KVkjJ35x8cVtFCBhvL?HiK#Zh#>J(`a9tvE50>QXJ?4(8Pxi0=~X=kKaxUyb)tT_SzYK$;;nDL)sfj^i@V!#*>Q{6z1^{cC%<9PbD1-gNBCk~RhPvih#1`?TO2)J5zF#eHXcI~V8Ax_c%1LBE)Y?*?P(4D_#MS#|igTp4@~@!v`K8Tm9mB>%VSAaB-Fx4~;!uj*pI=Hp}7zf)`6m*#R$s_*-W$cwe<An^Kz1k};ir84R$3Y*})WK?;Fy4x!3gMV9FFIvA;Z&!*x5OIp73&3mdTo9+&kdOP;x+(rT;=HpP`7}fO;@;Ck3&0zN@8QR+b|2?cZ10cvo^T97ezaN6cn{gSRHW~f1AVBU`<ghndU9u4r{_VeYfHX}{ul1qsIz&vIqGFL=y;p@a2TYe^akWj8{vVvYY$Vw+j2bV9A#%99=+=wns@4wv*Hbx5ah)y98LX_+7SMYS<Y0~C1=3fszzbIwuau=kFn(utyAU%@@$-qM%?;>`Z(W){VVtpjYre>Wn3J1u__AvAQJN)qrN@2fj1*Rg@4_?FYY_7&tCAB<Vwhcb=tABh-2|S@V3<6@T2)0!1t<Y_kg~`_LN1Rh%h(wt7sHSeLB4@`F}SC_nzUG0$#M6kNB;HH|QP+b;3Efrmw@g=KNUnvl*BG-Z<Kd`k~xsNr*2Xk@&#p=qr)634U~Y*Zb6`j?@pEdf@z9GkSx!^=d+WyJ9H%P0w8eUOT*l;tZdFe@BQhnc#KjhIEe7uG9BoQ{M-O-@X*pHzF7IdZgb2I^P!9TW`kW`&Qp?fY%D1P&`)$rK1n84t@y#kME&>%wJvUJ~>nm|8CLeJf!=udJ3JZC8@;Ub|m|t9OT((?2h-k)q5G;|8oSzQ`4TlUqdQWUAlFk_s*=qr|`2g5`ALJsP;GPr~WkXqD3!Sw?-WL#H^bFUP~@Tc^huxUbc8<fVb>gPv>IRPUO?{Z~hGSW3o^etwsjb#VG*1?V30In>(M;y>Ms@c#A_8-2+p+e?%YpjVJrpPPA_DT=Jj03cS_H3I5G0PIRvw%>b`YIS+e_$8O}o@XUHf_jVE8OHXUj_q<oL=kWia9_6850KNxo3s*g-d!Rb<X1cD+#(oAK2d_ok!@8E85Aog?51YM!yhHgB7dFpBJQG@jw}j<V{ueCRiF23Gp6soY>Af7d`5O3zLy3RA9dU|<FY%pYi;4tq<cuc&$2R654^3jo{;~jXOM5~8F4Crf*X{BVr{1wX@^8e)Q#?Vb<R|KL`o4LU3|{k0A^w#+^-rwlOXOisKYB0J|Gn@;$RB=9h<xm{CbPT{3gv~17(KkiPYH@tf5r0O|CBJc^?&zMf^WP3_oswLGKS`=y;(NG7F6Iul#!^wP`divp}j;Gi4H9NS+6P4M4|!9W~`TCU(Sr0%+-=`kSNVkjcf2)Y8^L*(lv=T673}VFqA$(;sc555{+4^ab<~t5}^`p8A|WSd-LYKdh_^0_Bnv(4P-r(<Lbz<b>wkdj!EUJ6{8X7u#`j{30IbCY|rufvfsfheK`()p6kzJKZz>5pK2`CxGMWp{+w6}*6Xlr$8ci*D(9Y@cTcWOP2P*z->0lAX(<t3C}S``tHIAJu`JGql6G7}J02^WiW21{%CfA;b*aL8YQ(6<HBhm2;`o$o&w3Nqo3ZS`y0YoUoRVEwZz@q&!b>7ZqO(MI)<2dAWEsS~%5?ze-k)`~#z%tsx44hhSoN6d8PzW>S=ML0D%(|OS=^6-9FrHz;`Lp5Uh#Z2Zo~O<W!{y?rC63`y>yAZ*5h$GmTIhew6&l<t;ez!>pgf}{9KJyzxQFiE6YC2w_&a&%QpPXM^N8)W3=KLbmnK>89w~{V;*;6*^Tw4{LGVOC)O35`FT^;Rb6Wfx+B~L-4E_OcH!scSvs>`o1Ycy<=NhiV|8cg#<8ki_Yl<M7S>fi+p(_xd|4mN&pi0KVBLwId9Xhx*44Z*5_2R*v7E+we||QI<tWzUB<4!|g{2zn5-TMZN=#>cI{R8LktmVGQjOP0gh)h6jAdQPz7nG)CP;*{K9R>WCE_Kfuw2UeTK2h>WfJQP*k>eT5p$Dy-WM#@I7(uf#4L#=EMr;U#%pY4sm7~#4~r#Mu$<5O*AicH4!&l&U1AH%<;*ST@iu<8in&!hF1DM-`ZTW3=bVc;ma|z`a;n4(mN6ytDZEF8@yv~r7%DN6q4XgVR<<k7iyD6>u|Xn1ViRK>bBj0^#dTf8`B=;OUc^|>+?+q{RgLFKL<s7$ehj7e=h{V=@Dt7c=kT23xpR1qvRC~yoT2njI9Don@eHMJ<oRnkmbE-qaZi#MA*hc>@HnhQu633(SRc<homwKlss=qJf+dDAf;rcQ#8(oVS*md&=XM$ASIH%;t2*@NS}56z^>u8sn&lU)hXmW%yEy!(|5EzbpN@;7<bN>zdFCHKA4|^cEq(p-V=^STwEB*c9|87go<8aeK>Py?8`AC'

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
