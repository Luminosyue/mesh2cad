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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_003.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_003.stl', 'source_sha256': '0793726855497645782b1786ffe8acf145f70fb63a8f4016e5042f0501d189be', 'input_faces': 350, 'input_vertices': 210, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.025868291035294533, 0.24041742086410522, -0.15593092143535614], [0.1587013304233551, 0.32076436281204224, -0.07271651178598404]]}
GEOMETRY_BASE85 = 'c$}qL3viUx75+((RzV&TLzN)QE8!6#$SWX_MF<!IVXbI^qHcsB6oilj6oj(8sb~bjs3E|jSRf%0!Uh_muqF!%DoAOkc2Fnd6xwkbW;#wgP91CS+5bDY_n!RDblS|EIp6vAoO{3j+;jhp!9Z?e+a$;R>E*0D*Y5KS6_RyulAM(VMJ0>o6%-F%TDYo>(>c!55Bpttk4z8DZsV+Uo=clwP&}_FZHzB%?1Id+bYI$nWkn@L`AeTzRy4nW_{sT8iVGB9yfDA8K*jy<8=8^s8#W-_x7PPR{@kV{gh#C{&mt|$$Ni3cuzX?DS@Pcw-a~OHB_+;Bzu0N>C6BxOH(7B$dVFr2j}|1m>oiZWcwRrc`>ZGL4|lP6|DgGCK0NcKIN$u|stQw2XvTMq77sn4>sRCX;owD=&;Hld_&TRU7O!<)xn%LYufJWQ&F8Lh*IylQ`I|L+&Gr4!0T!?Ox&7~+eCWuvMw93D!zG8}`Tl(=`{O!Se|^<F7v}Z8$4}b%crO2quNtj<^esHK#a;(}b6)(DmCt<${_Td9&pQ37-EID<t=9ZFY1v_~{xC25BYEx*^Rhpor%zey^Z7C_&zE_5zM2>38>~DZ_L?`%i+KxXFFoKj|IEwzmpsou^K$-uzRd@`?xW_#eRLAOu-4~u2@RQ9>BTp1t*rD~U-NSPmZnOt=Ve|#ujKi8nU~KS-nzKTtN)sp{g17#@|p+c<vcJi=Rxyw9@@89>+?J_FXvhEJkQL_d5(Vh=25Tv&b++uI$zv(oiFaY=EZ$yUfy@ji~Fv5dEXo6RD0fc@U8B<;Prh6->N^)T(s8b^JQM1FZ1$zH80LLdg71OUh}4TF>k&Z>ubE`pLsd|lIQtnUe3QiQeNYAA2l!Tqp$31YkmDaUcWfv$q#%j;<di!#rn;k9gKKAFZ1$wCC|^xe5?Cj`HiJV-*@Ik|D7DC&TAf+m-E29oCnRz`<|9*t*`Gp_*VB_@cO=km-Fn~wX4qSzB4cHyUrK)UFVDYu6c3anV0un^Wwg1Ufg&8_cuNJ!@TT|<hei0xBC63cmI=K=gYi2U*_fcYF_^S79DcZbKaPj-!G*b?S1+C9ek_rcfsrLckpulqu-WVdiXwSUjDwlq`_KWf4?su*%aqnW?zo))9droCLaPH%t`g+o!|N*UcB$0i%!J*Sv%h4uXl6#y7i|`-nrrO{srga`M#QLH$U;PmCwA>_OO*7>^95g%PQi0^vfO%CLaPH+Iqd-i;w07BVK$sbAYSo(qk_FYzKGWNy!Z+@2qn9=6)^pUcCR<tcVxy`$LAi{=y|z|AWVtH<&#4(|>wry%!%$iA213XYucA<L8pQ!sRnRyJYs0d1tiCb3gstHo5r|Kegt8d1un6);vg_=Rxv358-IJH4n`_);5?t&qHw9mU=JVxg3pn@uBZ7#GluHxWbwr?kDqle$Y?Jb3Y}|{R}=(W%ZNifqCvH&x7Q79wg86;D55oUH|)Y)_F1SIOpy2VjkxnEj`j;tph%EZFapE-<;JF@#4cT?5(xdUvu-am!1%K))U%r&7L3hhk2d{?vLcTKa%JEgi^k;?jxTs^ZMT5d?nB4D|tR&r|n;@_X*D@^Zb6``IJ1*r{sA)Lt_(S*8K4M7Cg^`e%}gSzi$Pv-?yu}#LWKd^8&B?jPnZ5y*p;k5BHOK`TmhS_fzuR&+tF`$ISc4^T0gcFP;a<^E^nN=OI`<*j*p*6aD@Nuip>+{ujJ{{|lbq|Ka2bF>~IypUmrdLqD6BO^KQF!}-kfJm~xTaKP%ne&2$Z-@lUA?_0sg=OJMIwQ)t(=(&IC>^Nk%I!VrgeB)1zMA8p??>{vz8vbAXsd3nd|NBpkYn6u8%GOYe;fs|mL(G``B4tm&FQ#50W=wvGvN_5g1veit;~;W=p=>U=Ld1;cBZqXY1XqHXaUpVwp}7S67aO<)Ig7wAM(%2Swi5dmLdzWN{V1M`w5~uOs0Ys}dsZ3sY@xCzl`U2Fh_ac=W-0r*vU$p8qxKopQ*9CIsrGTyQ|-@CPqj~>zChV>WlsYyKuq{C#FU?pngU?@Y?QL0%I;M*3^8N!gTURdY@)Jph#8a5MLy*YS2h+gWAfvH$v>!U3S!3O9|9&n9cxc9@O11o4nAAiXvB=kXF)qX*AQg`5i=&A4qc>qu(C|VjLF{zU8H%EvOL6$$xnkW()_Tp8HgE^|0%SQt`XROw1G!J&p`ML>_5=J8PJmn@5la`2KGZw9((}%=NUKvJu~2Q(6bo^&M~x-pP+0cV#eejfUb0KV-PbQi5x#P6E_(#<1xqyKr?Yu5i_2QoE&JLiv4p8JQX=v;3ptAfX}93-^tLDfxXl5T%<J@eaOan=Amcf(P!%MAe;-G$xxi*5Y$dbJ=H#lda50cdaAt_^;A0!^>nvr&L;woMND`YV#*(dn)`w2v)h&ZNLivoUm$MGn0y;>U6kFWtSe&1<a;5Xa_Qfb?m*0#d=fDEdzAG+%$R%{F!?@MyN7}MV6U$5-IaAh%$WS0&`!^Fi{t(z8kl?nbdlz^$~q!uO#a8vMVjwc))z5j^1Y#pG!IbL4>4o%{h^I?wa5OQ4BQ@i9QbzF-!X7I=;;WbjQu+rI2n5S!lz>Yz6MT(o__E>(X)OA?rCTx-_4<a%5-DK<bMKP3E(;-X50Ze$<Rz(3S!2ck&_C|#Q6|2PC-sjX!c?Mo(A?I=T7k5keiCndSl-dXlaMN6YyN5wHNx(9p~8>JxfBLsmE<_E_5a|U!8D<RNDvjRC^EVsrEM1Q*9#ZskSTX>2A@S-vxXJV#2o~ru^Gc(*>A5t5^2Evg67QAZASdb#Moj{YKeE#Ei+GM?U3lSN1Yu#^g5ulYd@W7%^k=uK|-khPA^6K8C$6!e3H$88Kt>A3-}k7yTZ52r*;wb<jncUsARXF=O&up^G&CQduct#^kp^7is>rvNMPolaD|f>1x9MmkrzmJ%`};V*f)1-U~hJ;5T9abq3x9J*Ds!*uT`k70`1Az7ah;W8g+ZEBSYnRU>9hz7o3Xz`cT)aW!%_K{Ii?5i@=TITg@M+)>1gcO$0}nvY`tMgt#3&PU+iL2d;;+k$;}L(5+5U5Do)t>@8)OE}L`^lStAOg(-b=R#-lKF;whYLB6wYM)0v)ow>U)gDJZ)m}tB-L0_W&N$(h5feUunDXmUa}bz5YfyGU*$HKDB4$i}54g9KomTcCV#ee@KtAQZsB9Nv#^g5wlYc?k8;BW`F9#-Hi?!b{a4q)w5dIToR}eEM|1q@FbG@hR2x7+MPeB)H-l=RoV#efu1zn^$q-+Ob#^kp_7im7MEQ**h`IFE_y3S$$D+WFXJxAd8WB(%t-VZ(N;WuOd^#<MyJv-p{VgDTl-UmHV_!xQ?HE_((O8#ACZzE<*z6!cdfqNA(<F}Es8JdYJL(KS9<m`iH;%X2xE<;WXnrpCs%)m9s`564W$lZs}wqf5gXxWdwPvN;p>j&t=Cpga?=-Ec}nR>hj=R#+40q6K0YHLv+$ZeC5l=wscOV)pWLh&zi^MBBimG+-k%*v%IN&m4Wkb4XLKB0b@NQnQ3^G^CL!1*^*x;W4'

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
