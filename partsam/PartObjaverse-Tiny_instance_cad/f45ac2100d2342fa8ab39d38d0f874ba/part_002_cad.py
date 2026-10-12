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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f45ac2100d2342fa8ab39d38d0f874ba/part_002.stl', 'relative_path': 'f45ac2100d2342fa8ab39d38d0f874ba/part_002.stl', 'source_sha256': '117387e93d2dc0441e13e89c7292a61123138928832d2ec3038b8aa9bbabfa9d', 'input_faces': 346, 'input_vertices': 230, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2247939109802246, -0.48359978199005127, -0.20810940861701965], [0.22478877007961273, 0.06011804938316345, 0.22478874027729034]]}
GEOMETRY_BASE85 = 'c$}r033L=i8pj&~qFjmzL6GRM0!aXo6^MX{11d`lgm6VbfkBc0;fhI!2Qf}WjU3?;h=7nmK;#GkImAVhCMyX{!o32b;(+I_tm}#o(YN}xtLoRYJ(cWx`*wNnd;eemyHZtCRbBmcJ(3c_8blcCUpr&Yj|1A@5@{GBni>&CPHJZM)JdsXU1w%IThF*f`r@ChuO*Hek~F5Ckz>q>PD#z0lo{Q}72P+jS9BLwblR-U?97QXC(O!BNfrLUiPN)EEkA3@#EewyI_BQ)-MYBC$98c&@A@DAH5PqnT3J&r^y=idg_`ZBFDtLZ4^*Zvdr)ZPR_S}oDpxzp>%Lvy^e>Zs;J~qMLOq+#&o8gT4}AUMd{N%}ZGrUN7oIMa^)>12Ew96OCB}F~dDqF8lt1OBz0UHwZ<i00r>b^mJiXl6AKkb6WBTKzZ(dn4-&w!z+x2^9hKG!sXYlc@<#qXMk8PFxUwoq)xB06oob?-xey(<or>k%2);j&d9kL!{>Urs#^~S#=?>BCHt)DEvv)Vb%z6Sr;US5aq9`*fp+5c9rR6EDP+vYu4zLr02zbx;YnXmej`uCa6c763`OW(+dJrvTP?5t|%Ji6aam#X`LM(L$;{6}Y0JLl2%jZ1OW&ha-oxl}!x?|be}RX*w->HDe-Q`Yl-xLRN4b-#1`efy5@kn3>q7t;3}yt_JN-k&|=59xpSqTO}*#<?ZCWj+7g?01f{E9$}?ryqR2R>kg<zxS(^{*d)nGey;}`Nr%ivVPZ!Lceo8c&<gtdW>dye&>9-W6ET^?iX_X&UIoejN4UShwtkVw@dc()(qvBtUnqukNx6R{oU3ak-w|pFD0@bUyR?m9s=us+gX?Iee}1T@_96){2}XP+I3l8_kH2lWqI#`%SWB_;_;-FNWWi)qt1SspC`+Dbl+H*tm^sU1KDrGbMB<`ce#77KjNGhGq!b^oR{Yo9C41b(fXHzvj4ZWIpUmO&-Kq#`3cvmoa67x-&R&$hwqNvCd&sVlvFv_k9X`h<>htwzWU#k%X!~Er^>k=%$l{byzYBuua)J^(*>0w^IknpJ_ow*E*@vf@wu8?>1@|EuIP|lKkvj>hOE!XOzC?(?n>wU`sQ^q%j@us@ttJ-uB3LA&T;eg?^q$%ZPBlXL&oPq6Y0D2uN-#Hi_y1I`ew!1!_IjL?A|AR&*aLAkn+h_4h!EmY;Q%#^HOwH`mPxrE1dl?+qbKf<r_AwaQ4SH?N?RLt3`)Gp7$fUvb@<p^H9k6L?lSx<7d3>{dseN^j(aTJwEQ9Zs~i+sQC}hdykSTS%0;fXS@D@caHP}iGea_|Gj@}eMHvpRqHPJzUy&KmUnwwmxYW^^Yya4k@3qx=lFPsE|9+O``CTX^6pcc{j&Zct@eeC|I|Y1`$nJJ<Lr-J-pni8<Lr-l>3QjUZdLoJ{d+x$XQc0~X8*JI^8+iTZ=|<X`_x-&<@mXm3|ITb>BrT6_Ty-I?d#oLKKHH#YM%?P|B<<>9`+}1^NwnM*r$R%^I~Sl$nx$7A6ENWMv-cF<Oa3xpT1A}u5PQ<KDXei+!s81)%(r<UFM*yYB^uayOcWn>Fu4X`Wd6%W5IoXUz{v&)>rTC;CN2mC4Jv*>iryiUaq_>eea_x@37~~^-y???0+AXM+E2h<Lk1#s~veC<$Zy}HBLX6?|r*P)w7Pg$zE^8%R+rSPgtHReQyKx{tWIXW<iJ_oZsSj=^H=A%KbR_K6>DMwbKtiFAwD_f0W9<^!jaIuiyMm<#&4jgTB^(w_oM6`uNzsK0bk*`&Y>OksB{cpZ8JVOv_?fe(+W4d#|U--{&grDt+VN&!5QO)wceAsR@N|%6=XCt1Ryt+fF_YMo#|?PTw8&sjSDmI(>t)e%E*7)$`E2{zloKm2uJ!O!`dbQ$|Jijn00$8nXX&Z?;K|=aU!J^U_u2*Kd6#eQ&t(15>Zb=h-xiH#_V1C0<qjB9))&>&+-u`LDh{T{Bc(sjufivdT~O_3zogwZu7YUSGOw*PW~KKK(iJ-lXzJ{dsgJsC-0!-aS249;ELZCi$1XFPY?h`aWjFs{Bje_X6aD`abFUN#$|+zG|*kd7{1#o8%+<zU}R#@|Rlsd?)e_?Y-doS>-Ra-Xl5W5!!pl9j5XT{XOO8J+HsleB>AUdoVyAp}#l1cHW`AXMN-a`g_?Jpz;X)J?`G4@&f(6?;($<l_zk&R$jq<Jr6OatM>K0#aDEv`W>ql<jHdPj*$6*tApy7p8xpl_rI1$>3%SeDu|c9QC%g!TYT5z)b|bJS1V6r{Pesoz&z-ApwS?y%GrPS_6aI4$yf8Q=b1)N=3mQKP1aYfyqEQ*=g$Fq{c8EP$6mi$e(tUMK>1oe?+fp6RJO0>|A7@z>bcavJ2c<^?r_ak`+@#lqx<%EjVnA}J>PsExzBwg_bJcUv;5Bf*!}d_`-=8mru+7HnQ@u@L;JpSrK^2H{~iq3`;+$l=w<(?^?iz8>-&`btk!pK$`@+C<hv|*9<t)P>JQ)7M%sxTvcErcRrw3w<3{svwJ+QGj`m%z`}TLed3T1|zwPq@Z;D#i@$Bo`IfL#8&l%2USBI<z=EX~XQR{reelKa~B(;3|oP_t4eh#Di_Bl*|d`Cae3Gn{Z&xLCF_PJ2XjWy2k51ub+zCB-F-oyI&RV|<MtAL$PY3F0QZ`W^<PwD4xx^JJq8Jk|Jan5hB|C%3MZ{&UY`JwIy&jZQ(^z%vG5BBGZ%J1~^Pu&lmmy##y=c~Fe%O{1LCKs$2>fV2gVTicNh%nM7I*yWsDgN17_fhiH9{<%*a`zr_|L;+9zSV~pt$5ywSH(D3F&E8)^SD13eGwL#56|K6UqI)=b1CxzWrRLU2!4(boQvke`Lvgd=E1qJ{kM6JI`ioJII$+Ic+!egD<)Yn-io)Z*l5Muu+Z&Ryl=%REBsc3ThYjh+pOrsbsO$iTk(k%2e>|he#*Ul=wbe@wILRPVRYuYEqWvOx}kUScYn0v&sOZ^`UCVs?(IR}v*P#stqT=Ps*4rf(Yq=8Co6Va(F6Zpw4D__>HkG5Y6!vSt$3H~O7uJ|^a6Z<a!1ih_!RdpqDSG2@CmdMJ^>#?FTkhK%jgC8GW-Q0IDnpq&(mH2Jpl*cv*<C{ZtpC58NN&#g2g%!Yh*tmxQg)+*B_x(u+Zc1Daw6@egvOF{e<94=tuA+_+#`q{5g6CJr19N&k=%8qE&De?VUs~!6)G_(T`!fy)V%-@EO_=yv>RoR%|8&moO&cx*RQmg_gqaQ?3FnhqrNW2U-E|fK9X<HsOP4DO`r`LQCOY@H>RyooESMLVG(=6W$3QLJz`rdxy|n@GjaAyxNL4tXM?|Uc>l^>n-RSSm;`K8|Aj5Tj15)djs7HzX5MTx4@g=4d_~UJz9*eg^OVyA$T3S23|vZ>(EW`I`~a=18leVCRz*^(}v)MRxGk&0U@}M@e$WWXdx_gF}#{`ucJlqLhda>UxydLE72l&CA<P%48MjhMHj<M;bny2C1@dBNPA1rmGBaHIl2P2+gpw<g_qKX;HRv}vLcfZoXz-%>v?E4EHnpRNV)mwJoqW@Wuf!oEVuxj2N%GvpgHhM=rd>z{0#gwA$T^L4QJEdY_tHL4Zn=O0^9Aqj6MTDLmPr8Sdn7IL_%;H<0Gy!&@@=+6!<C1%|bKa3EWFTXTd4(3^W6t0nbFIz|+xmbPAjfPbCCTM$_Ol+MA5dfG5M#(3!B^-ZV5FPNxmQL#-HQMG_%+IO8L(pFoGhLPx?ADEBz}1U!^`!_dd!VelCA33v=V799zXMw8Kza56lK5Ih1M4iBfj5$G6r1pF8}7Pi}a3{8fUX+yBvivCtSOb8yp_=xL7bO0=LAUu?EL(oLn&AtBU5V${_fF{BT@L+Tx{3tpI9S9GC|3C<S1RVempuI=X1o#m+9vuwZ?Zu;m;6bz@SmefcS#b{`IGXVh*Zt6FSZFNlrd(gNAKaOHccFdZyWn1EKe!j%2aSdALu1fbI0o)O2yTx?!_l<Y9_<CUhvU#bu-#r98Ux4BhG6kcBEC(UF(%^r4zw98v<cjqa<`**z~S6$gx(G}f?J|@z%AicXcPEWGz@J5hr#s-!41)7a5LI#h_-|q!Z)L>V7tAW(J(lSHUx|BHSw+1l@J`o_=xMKXcR0o5)P-_4QNw19Bo4gZh$t08^DdxNVq=Q0*!=Qz|9H45oi<~MSBrw12_UU(8jRco`JT2ThNC1C(bVJx8fl}@B@sAxbBEP01NF6ccR?ytVl|zS3e@`Km8ZFfB*A}i3#}+b^2e19+x=(GSR9lczBYO(C`NJ!|KbIYJc%`8UF%PFO<y'

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
