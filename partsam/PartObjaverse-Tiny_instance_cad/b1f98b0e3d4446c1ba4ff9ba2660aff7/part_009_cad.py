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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_009.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_009.stl', 'source_sha256': '7d46dccaf1bfb8e9938d2ec0e64f644888ee28551d2be9c52872cb1061e35638', 'input_faces': 360, 'input_vertices': 278, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21702153980731964, -0.35704362392425537, 0.32498598098754883], [0.12722286581993103, -0.013317093253135681, 0.3901064693927765]]}
GEOMETRY_BASE85 = 'c$}r03w+MiAIHzkFj>SBU3kchu-r1F{E*8i$)%#`5gSUwNC|(xb&=d{k`x~1ewl4HYp%Z;=C+w_gwXy`>#}N<nlAY7d(P)P&N-fX{a^q8yw2<M-h1ac&+j>x-{m~|_3^J5%*0Ov_CVi=r3>$7j7l{Y%qB<1Od2yHa$;EY_$hv@2KV$MGrsSjC;AQcW0Tp`(2<c7N5q77bcJ?`Y9HF%6&f`zW>U=X=oiMtjEp4TWBAyKk>!5k=;7ld%YSduI=p>zSDU8IUDI9v<4@J{L-0JGeQaNOT5r_Lretx)3p@Mpu8t|6lD9Y8+_T|Vj;i%dFY7y9W^nIHd^Ag~?=%h<^_^($?FzejeJgwdf4%cwa;{q6^s;^FnN??>ulmw^k3VqG5%qHw?M&ysD6%#8tmc+<{yx3ZxOe^4l6%**t=zl6>2ikq`n9=t-g@__+K!bL%)M=G$x^*1>GQ+9egC^pYW>jTqVRp|a_>1Uj?>-pnD8$*_(U6*X0HgJvVeP6Y#Bcu%YPX6o-uvII1X!nnt$FJA)<c5xg7O)q<5Zr(b0}`caUhOXGt>u`?Fa-y`9s8zpowd&%HhLtE1Zc!pr0F3^{X3^=x}`mRi5ay@}Uz2b?;p)|cL?nw6z`clu1xZt&6!wI5uuzaHZ4jvSh+wlBRr9#`<RQ>wSdb#T=BY}h{Tom$iL)c$dz61guL5V!Lm{eAPq@z|@y@uYUlRgd56os~zm<AHb8D$DZa-SwY$)OI|rKIGp1WlO#`PYf^Tzw||KXD9orFa6)uw@RK7pQ}|*as0LVr>OmJmxUbixxRibJ;?j>^dCo5&))lyd#l>R2efsxzxbfqj#CmVjwdu#_)euqG`}ZBwEtX>1FE;CZxr>53Ubu`l-_ypfTMagbqe?HYMZyKpUX403-_*fvh&n=B0Y<%zEhk32OA52-+|-Wx`TJ-PRZ2#xnKElyY?pLY3l{PD7FuuCsshH=2??hcdGSSZi%R0oOoRA2d~eZpQ-gvn+)!)sh3V_{SWVs`abm^J?6Qy;!f^8M@QtT{VBb@s(Frj{L;IA^XyXV+g1M*=Y_{!JfW?xyM7bix_^T@Z`t@#ab94x3i<ntOcI~BxJ39QXODLLhri|CeZ5+t+K$ujptue-?RG-#AG<}mc;9K)_Gtdc6j6Ub#71?Vuzedv{dyVvI6a*sgdem))c<K0_ulJWZ6@j`AK9X{Q+8!Pe|@vCe05$)?@V|tRrS`KRPNbtLHX)@klu>8nySr{)tf~91BEBlak1JC<K9ll*{1cI=`rq}hR=xOS#xiJTHke}muNrkLY_~5TR?`^{_48i7acm1r_E1zPx!zL&F}w}&trR0;z?~?!@Gu0+@bkinS7nQ2L_+i*3sZJ?yZE7Q|f#$z4!hBp4Ew8>8rl<vVPILC%L!#<m&6FRfK52<z;Q%IU7So{iuNj>i9};1?}0U`L4oy#)YM+{Zq880ryVq@sq0egqQI9A$xgPfjS?&e$%T-s&~1s?&a_IVC_O}9O3P-?i*BZk8!wn&)A!<t!sFvVY?J<T(ZyY=AX+iFkc-Pm;X_IUT}ib^0oJcx0kF<*7_}H4)^Z3W%=somEH-wBSrK5=JE5U{ngo1+IsYRQ=Cr&0#2*r>m*MW=l9B^;`#CWC5!vCMx%s(D>GiL&nlOQ`8qzVP+Pz7c6RXwZ5-FF<K8N*Sg7{D^!C2?o3!=I&hq=eqUc!#YJW=4j@_H6dgn;K@L?CUadZ~%5&mHJ)tZl;ovx0f_q_ehYQC=QZ=TcEyEAK{@MC)>YV%>n>)bovKU$#nzg;hid#m?@+q8N6`!zmJ?2R<7-@HC1b&cxX4X=uEbxqdB%k*+RO3$u$pW~~(^xo%}h|jq96wT7d1>Wvdcbzsa`^KlJ<LI6Lqw0zJ3%Z=r`UjqE&0Vf~PuIiA>N@rIe}cd8Ba-y~hi7vqZq|JC4}3j4*A{90FTI@+wMF%=Mhn;Tc2d63`rqp@F5dG4yqxFW`&D>(9`mki*$&3hY=@=vPSD1E@I2nX_MsKp_<DU=q}HF(d!lm-e0e)@o7N9(=4|0}&hqx<bDuq~=?A|0-+gW75?}o(z1g2ulh#XojhFQ1coi+4zS!6NareIv=W8BHZ_YzIu78}bb>#KtI+~EV$k+Uo-khK8_O!Xa){*JuI$~#*cjN7QI_UjxC5H3*?QbM%-tOR{-_7$6vnK`e{`>f8tv?yt-J0i+yR`EUs~a_m_p5oH3{JH>vs=%%(%*8v4Vf3q=jqAQ+WC`(x!&X%9;BT=S?$lczvcW7Z=V0zNAnl(Y|vJ}ju_tCpP^Uc`S=*uJL%2qojtI4G55yxRC@DzYA3kf=lx?`msyMSk2^CT*Z0=jJv@#33a>ZrE9~$B?#=rO>2JBO81}DKJdOJz>CO8htInVVK3+*DwEG|X(rDoykI?Ry?8~2Xf6M*hgkKWG`xNW<X`L#s5$ow&?Y_>wn7)>OF7y7-@ZS9^XU7KqcjG?RW)YkDyfyBJr8n<~?LO~tZ{E+d(k;Rp&jr$(&jrq;N?Z8fjr(@5H}2c*1tHvfzHsT+BfrkvyPPUX+PYYoDC(QfHSp$hjc3KuB%a1|rS#@=rSwJ7FK250*%a<s?<)LxP2TT$nqL&Y=3m<LopbDp@G~Q{=RwO8k<9;oevkfKdGQJE*()*n^J!<dsP7rAKhM@4oWlFZc;1)ZeBPJdGym}ezPz~)V6VQ!z4=@(z4=^U)Ui|?kFmcYz1%mG?<>8z?_r(ky`BHv*njYPbN?ZGFZbp?iS*_^iR*cXdviZWdUHR=o|2!++wWVZ?H92JO1XCq_SE)^Y{yFD?Hl_}R*lEGcQ3D??e{v)7*W63BijCzJv@bbbKlSFjeS4q&3!-V&3!*BbC-6U-s8D2WCw5G*#DH?-2asRmi^C_3EZ3egr@gC7q2`n-q&8B?TcE|iiIz;weyK}|NeCTxs3f@>COFKd)A~+c$)jn@VD$U!<+le_UNV=YJKnL9lDEqbDvy#bDx~GskDoa*9Y~q{dwp5V(zUmi}ddWGBbpKAyNBYfVC|UzHq(vy@S*Dp54C2*WNT>FMpl!eTV7gxVR?xIefe>j@Q0taZdN*p5<6KznAH!eVeti@gBGPj`ATYFM%wWMGaTJ$|6ZWGJSuQHKy%<^;K4zb}j$kud+Pl$M9Zx`51+G7V=f_EbwIHaPVZX8`%r&2KPob1@{IwLDm2_0ar&>23H4HLi&R%fh!>Wz!ks@8NhD-5LZM7f-8cnAa4U#0n-pYfNX}m4NO@Z+zi|tc^8<n8n`*Q1+pf%1-KpZK5#p5SLFTRuHY`nhTtyXA;<{u5b*OT#E+v8cSa%Zh-?U^yc0}$JD9R1xFcA$L)-?1xD^U<81i;7WmPa`5Sa2oa2Qy&L);pL_)!$%4#*%dWiXhs0hqD}xC2<WL)-_2_&F5f!N>++N()T+ESNG9JQyt7As&N5JQ0O>0`gff<ybJ~3^3)J;0a*a4)NP4#EVgg<B&7JlncO=%fXZ@z;R&N4)ID9;?*d`Ymm#ql$*hn>0rtf@EWjehj<$b@g5Z7eaLh$<v}pz88GE>@IJ6?hxiBz@ktco)5tSm%5T7w75xNLUWTV~S!sv(-{s{8WGV78_%dE!io6X>c{`Z04E3p$p}il#S5Sz5Lm|F~q}N|V-T|hp4yL?{`c$qe?GXQpLi{5N@lQy4{ZGhhU`l^5<rk<=<qM@9;vy8{d=%nOk@Wgck>A2oo&{6pfIkJxc8HIn5bs4Hc93Vml!w5SpMWX1gB`GJhd2p^I01!tE%FmE<reV!s27i13to#l@yLZ>N*hf17C0XKJ__+WD8!Rch+~j8nDP}c<<nrwk>D7xY=?L>3bDM75D!5<&2C<6h~@Q&xGVA*Fl9e>^IAsS4*3MTdF>-^f$Ym}UMq>4BcEh9udT%LT1@-^3UN>52yjpEi^$i&FM?l3&H=v;o{dZd&jxQr?gnoK??Rpc?*iu{KL_W6FCi=V3BCmO^AlME><11))&d8CYa)Zely`#PEpKyLd3gi*GWZSfDC9u!C~$w|BjEnv_Q+6hd$0?6FW3dX8(9~8H@Ft^9&jyi9b_YL9dJG5!{B=0aO41RIQS{#OW>!#QOK#_DDV{IT<{d|OymdPncyYJ_24DojmR|cMsNl)3!DMYMizpz!RL@)g3p1!L;eo_4tyOM;3xPxxU!$fD&WfCs^ujRSqWJMTnYRq6NUH&G5~x7?f-$K_x=Ng_-Evo;Ge<gk%i#%;5=j&I1juZnFihuPDQQ<r-IiZKLD=-FGbD;F9pv>P6f{gPe;B4o(_&i4gg1khaw*a4+VEaHUf78w?*CqZVL`U)&+-v>m%<4*9SL7hJqV|A3{C?ehAzhIS||(JPi3Vco=vbavFFX_+Kc*^N{a?DL(?w1202v0xtt^K<)%@0PjE^2JZkLKz;^306vBM9()S?HIg0>zsB#xe<1_GftdHiREU2;(i->$h4>;0aWV1+xENf5`~zG9{tEds_$%-Q<azJ~Z~-z8TmU|X+z&nm&P1kyGr`Hob>L+1D&$h|D)5KM`QQ)1i;&a7i@>qSXmBieJaQ;_Jop7<H}DJKLCCh?LEy)bA>hZrosjjx{rdP-2=@QG|7v{m$L1Rc>VG^oU#V~FsISZ|Z_B&M)2~ke?N6`@<^Sm6Yz*C<u>Szd2Qnc'

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
