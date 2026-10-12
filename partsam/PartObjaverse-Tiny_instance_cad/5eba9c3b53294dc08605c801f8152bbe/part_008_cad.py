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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_008.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_008.stl', 'source_sha256': '27e2c1164b923f8fbfcec8ef2de5cae0ae671bfacc0acc6473f84fee500171c2', 'input_faces': 234, 'input_vertices': 185, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24059993028640747, -0.08160072565078735, -0.2176518589258194], [0.28473785519599915, 0.46019917726516724, 0.2170930802822113]]}
GEOMETRY_BASE85 = 'c$}q~3sh9q8pk(@WM*n+rUE*sh^D1HB+Lf~QLMNkLXzNvK_2201jM%;k(4k*MGIdz2tpvJD542EC)5%(Q`4?!<*aULbxo^lWmb02{=PpnPIK3~>)u)GTmS$0&3DfE_TFdjvj;+hTR3(U{BaZaFV1zn{J0P@+K7%KJw7FEdTe~^vvZOcI*9hf<)=yWLdK5?jdT#{VzEbDd}?fp$MXh{p$UE-{S6)oNhxV5F>|7mQsUwz4~m(U8n5%z#F*rG{kV^(-=O{m@4o#FOAY_yr?p;!dhhgEv#cd9@l$_YEPtFhE{`qkKKOw6)NaHz<;Z*TSR1gAxcW`bRms)!*K3L28%A7Nd5*Za-GZ*8Rg|0|J^2=KW7Ut$FHC2?z2FL6|HzS}blkNkaS@o?D7g|5zuz8L#mN2i{W`(dxz*(|-Pdt@o!N>jx0xGuFRi2eQTtC*zEfwqj@J912kE$WEpc)8xl?rg4R;PoHO>60fp}8&8Ol#CJ7Tux$;>S-Sw|>8=PBkvlZlI6$|18o{+P=ly3a4|iK`jy&(ZY*Kh(@tT&!Sjx>Kjo_doyfKGhrFhPWkhIkmTmD+$bvrzTN*)w)W~zg+M!^}}b2>djVMX=HBno>5QzbGv}JsJqSm*1DX=%alKxdDKnrhXsLDr=eXS^USjK#0~kLbU*JQxK2?8@p0h!CG;Grj}PMUN^JM8H5VP28#@0^?KL@?m^)|ixL4HBvGUb?=375rOZ6{nx5FN{xHc5h^%^HKzgV=3?i=n@Y_`L-@6AP|SH3+#eB`JN{2aYS^^0DgG0zI5=R<iF?Q&0Me%xgvwa=2j%^nwSZMM<<TRAZQWn~RrXT^acvpw#XMD-XwZ_+r3fz=;Tdlr=)qq@RBXWrumKM%eGXneJxZ|QsS{UsjX_kKEN%~fzM{flGNuV4P1^DPZo#Qm4=HQV9hR`g!V-vq86Xa0Hy=i6{?0`iAkWM0?0OscVg`_nSxF!Lb4GRm8`u*x16qavzEgTdGM5;uN7pYs30w{yPX_Gsn{?&i~YmtNjww&rQfjicAo_^bWEeVCj4IKP<>WUe~oQogbDYwB;&JN5t_Ur3>Tu;psuSn3DEZ177l#KqZU%D3gl#hfqPUS}Rtbd>tD7|&Z=7V}O!h+8&>c+v6n@yu_GFDG?>sn{MjWIS9<bs1k~{!;{T#Uq6B|H4mlzT&&>UGATBT3-y;x6pXna?L-I#z6_$%6vC-<I)1ox8atq6DZ#h@gnn8S7}@gV(@yiJ)T#xj?VLEuFm;{xT(^M@@=`{yPcG8G`&XamN+@!13JGpliF!;UBo<m@+InbuVpk3jkm6usooo@^d1z08Vl`l?O(aH&S-gEi3?N3d}@#7JiotexENVU?=RDoYxLd|88>&*`Rh(ro9%GLzqFe4qZH=Z5wyOjP71ZJnXhDSnc-Yzov*ds_zBf>(eZ)&Ca!r~=y@|PsHFFsSbdJ_(|+Ac_1kh|SuWR~GmrVBlWCrq=5}Fi;*T)5Jb$j7`n&O0eqY^qh2Hxn=TKg+y3Zu8ZkWXThcWXG+2f{)P<n4FABOUKe(DeBDL>+8-dCipru~RGHJ<8LueRDu^*^2U0JoUeZlZP^zIT}T%@y?i*2W*CdTqIJPa4g4#qcTfhJVmFiM3;R-dz|)T=nnzF4glk&qqVgngjH`<`+iwy9eyI$3?aa^{3h?i}~;`c2GUv<<Wg?xmu9I&x6-A=3TGQxGQ~pd3>9AC+3!qJM#KjSI>0^I#WB9tGT4jJb=08H-^{49SO|S7ww~d@ZZM$YQsg*0^W~xS<2sE%jJ0&7GN^l;UfC??bJTsYy0T9s;HLw2mNo$RrJ3xCW*K@{A>PxGxxti<neVoY&Fw!wwe21t#RP@()m1kPAoH4p0MWP0&|md+6k)XUfgctVPk3C(;71Ay==>kc|+*EtPI=7{TH@{=D&!XNp;zBtuBcANv*8nbvded3+1(p-)XkP#aU;b_YG^AYxO~-cLtW2?Qmn=4bFFdmifX))*9{~&9#cwU6FE~o&!^9T9rL+cr=vPjfr<liMQFq`zH^)U#2dn`-?NZX<ms&zP{2SnD;M{F^8$0>pcqXaS{2MiS+2@we<b{3pB5l4jXICcDSfZrG1b%wJDAC_(Iy}h%-}p-v+LNTin9lqwjx9qy3*4=6;O(AN8;3Me|;{lu7$c%k_`;*yCzx_8vNaNC@rM6xSr$cPY_N@b3h04cyYs;WV8$C%=@=>pYa}ti8nZ*M_SJ)ii&_sAH9MJnRQv-#$If^U8)R!+8ByvkG}0UpYqmH_<Sb$G1-$uODyBJWD#r^!@`phq>{3&iiz|+k1KcQ5!_Zrtp5WJ~s0@=9WJm;rVy-#dnAwY^3>OaQuY&p^2;DT6F{UgW|G<)=iO_&i%72g65ko*RFZ;KIe@Znzv&85_<nCZ#wZh3$B8TfG_!e+7q<SDpf--QvDmz4^elCtM>}%Ij~H*PyMCcy3hRQTK*mSQW-!0He8fvQodT%mwpea_1V-O%dU|p&DQ)Fb8V8>Nz%FJiHn&x==YIvRW0o&n)xi|ieDN1u2Folj}w2m_(Q6{XBPEmGj9ccaUS2NPd$x?XyI{z?*I8ae0^{g+<@zAKTc_&{C%lZpCNGq)!)qbgC8Bu^?wn|yoW2--}Xd>*$!7OEau;H3p`Kpd|pZ48~d5~{oBN&n46a8QhT)eU-@_Sv=gMpf|;kx);y89<xUi-c4`u}TlCMReVVB^kFSW1W&WlwttZCCu5VLaIZsla7(Iv7a8spvn)wUN#fW68$MU%g&(Df}w0|~z=S1tdDuQ@^Dk|ssOyhBH;sMOn)e+o(?t`h{^##O8b^oTXhoKMrRmkz1wkH=ns{aDf;}OwOB*a+#Nk~HZX;S-t5}NMwU;RnQ%iHJw{gco#y@nJ$(xG$UrOtp)hfhREABK>A0z&#J&^ho^;HN@U;H4(PPlb<$&V-MKk3>ix4xJ7k4nGze4=;5Z{8;#L(An_g;9o&VA0wYJJ!17phNi+N!>`a|IW!ZR3ZDr-7a9v6i)+t?&W6u~s?gc+D*Qs|H28(^OQG@bOW_wor^8E~4=;5Y{BoR=0bLBg7&#fpk-7vS{UYcxc&X{|QWN2qK;xi^@Nw`V&@gx}Xg_Eed_Q<!=mdCQ_~Fng@WbJQpi|+4;73EF;YY*!LnGn+;h%$s!#@Y#A37FZ>NxoR@ZQi@;Jx98Afyk3#=uLBg%5-uhLC;))Ce#8?Rh;Spd;W%ASVJL{VZrQywq3Wr7nP<1)l(20>1>~mjDfcPk;}#8p}{<1bhUp8;bl;9J}k$U5_4m^oAM`(szM&hwlRKsz-nx1N3+iA^i&o=@n>Ccm>`E>I&}z{|vM{{4?+a5z_lX-QoS<M<S#j3he>k)V84r=|>@?9}G3X4~F;DV~`%t>d_7A3Ga!VZV2f+L%YCtL3=twd%|~ycY_XqcZ2T*4S)|o9lfC4;Je{ky>M<X9KWf@>w4ruH|nuQkBNFX>G3l3Z}8cAtk+{3bT#}zJ$CC+4Yn26l=?P&E_^Yx8onCm7DIQyXW^U;&|>&v<VZgcc{vE_^PwBy^WjUNJK$x_d-W)XmcW-FryRN)z8qejSEEOz9%b-S_dpBb_rUMeBTbJt^jHOb3w{-R9&{)CPMn*EoIH%n8u%h;A$%e3T?DO!&&D}hphfUo;7g&E@TKtk5tV44+yXtOM>{>9)WccG4HNsPaokl8xwUGgM_>3RCXYSzcuJ2xdc1^?elpYpelmP8v@g6=7c1Wh$1d;=P)B$NcmZu8{`^S)5VR${R44e>@Ga41+4d)(kHfdsql1wDPGoHlAB>u!pbqd+@Drgz{5j7i;=U8XrJtn7cs(A5j)9jsuL&O8?a;N**WgWhtP?yJrLKfu4KJ^KNRI=0>_bRj0Ih&8fX~IbQa3{@;H6f<uZC`eR>5aOH$ki5rS5{yhOU9`f)5RLc&KBG|MaiiKR+sUs`Wp1ZO?pgyKjAFCw%~$H~*o*EuDA}9-@t2gItltzX7xP=UM'

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
