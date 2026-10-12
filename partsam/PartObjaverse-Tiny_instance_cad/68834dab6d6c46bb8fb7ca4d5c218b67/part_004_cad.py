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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_004.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_004.stl', 'source_sha256': 'db823a65fd84ff85b9ae4e3c569c6ca7eb5051407b5cb709b466c6ba7ef272f6', 'input_faces': 242, 'input_vertices': 188, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23735660314559937, -0.35185444355010986, -0.4721048176288605], [0.3672943413257599, 0.13718879222869873, 0.14286154508590698]]}
GEOMETRY_BASE85 = 'c$}q~2Xs_b8pj`fY0`oqQU(M95<w9HNSQ|sA(RjakO(*-g&GJ65I_Pi29atARr=5&q)alYlQt1hQADMRQbuKEMX*I(%Mo|(|NCn~Hha#V-JEmJ|M&j$y?eiR-*@kOGx7JUQPV?{zxG<owd=>4nrfPA4KxpJad`B?S)t)E-RDIut)?}Gum1kjEn@@6_y<+f7HcnghK0w3MteSI@*EJ+*VD`788JV4VRXp67w1QZg)4tV$lRE4w;wYzBr4o}+~t|ReZ5T2cJ(sFnf}MWdhQeqd&v0`rGI>AQ>xv(cvY!x+x;GnpZ=*3pWplqzLt`BPO0<RrDqU#>#2{R$&KJ^-<(WUYWXx%{1czN3-t+k2j|`Lfo~iOfv<VqbSSlcS_0pBXer{f9wDcdx<0)u{Tyro-|$I<nr`exKE{C?XYu*)Z=l*|x1|5Q_ut0x2szJsYoPSACrSM8$|TP_y*|eAuHWB+cIi-nxI5k9ySDd+@9eP@`Izo>h40*&{wCswv_C6;XZV(+tC$z(kfHF6+sm)v^Z0^N#D8BS4gG%I>N-AOISIbe<w=a|y8p>1IF7sOlzEteah>;e!Z$5XfbSeM2G?P^w+OyvSu=?@hl~HE9r+j$W6~>Lul1)oH*tR0k7+XQBN*56L);C-g>8fH?B3_J<okEYb9%VM_g^pb@$FXl&Z%wCuQu>I_}2UHARkT3`gxH0e83s_mal()$k+PM5dXVV*B^@KxYqAIZdCOD%+vH^%0vF2*Jb*rw_MlSCsNH-<fA8srkShA-<nh=ex-RZZT3qyS21r!t!7Sh74xjsNr3-v_od#XQgape*Hym&e&u@5TVFk6uA+XN?b6>gS5a?zr$62@S5dc`XVTjh^Z&EXon7vWUuj)fyl$LTe&uy!daA`c$iMQs>lyMc`l+;jO}##WUwOTodN(?U_)7bO(SP@Q@GI>z#-Pyi7`M{C<TRIx|MsdYI9@QKP#wGUU*PM$U&=ml%Z&cDp-Jy!J|};Uea>~p`62Q>yyFA-X|+GVu`?R#I=mmgVT-}BX@z$Q@;h<}z8*aAefVcyLqGb_Y9As#cno~wObUGC*iiA!38)8W+>iKNKfVaQQ!kY|84@pbbK;uBKM{%jKwo+X`Rd7K5+B$I$6BmyEsm3$Ux0QPjCkkpK-7~pWe0riv4C8h@AE!<SISZN`ZKp=T~Gaa8{$%vCI0rwWcUj=%D$g^629pzFPZ1@9kOtKYO(Zls>fwqXXxY|$UF62_(tiQmvFvOvm^3Ly$;`6;wygG$lb^*?FSjR=)gtzgPP(#8)*$Mq94c47jQg1ARptWwSw<Fy$j=7eLH8${c8_j&x^hw^$~=9(3RE+zIL|%Vf5qc`v&6Ddx$@?F7nnR-<Ri5`m^w@IW?pozZs{HXL>*QmQn}u*QYMQycy|c_@?Y5QU??Nz`k!u_mMnH0_A$0EB!Hk`e?bXc31KcA3t*+;?jd8pW^E>4>SIO`O$2V@Ljef)S(_T3HQZhi<0Xt=!1CYz<RcdzINB^1jd;Wgms|XR>-)uA~G>A!RL<PeA^nyGj9v7R}ZO&dA8biiJ#L5zGiNN`7~uDOaIviq`pTrlljTW7XM<xQ5=VP97q2dc`~kj0OFm2pUe9~hC|{r_Ix09csEDlo#OkSO@a=83UzDAI3@mT)$N#%sb#XSXIz#%)5pmC%xiP5qHhG%$9i+EXo-0?W!{&5dc|&fXdW`FUqU}YEfB8-ZF*V!nwKQc?ULt&%&dp}DH({j4qIid=<AbW<$Y@Kn$4((%sSHl^E+i-&GAUV=b7~--oF%i>%l#9#cwF_V_L}jRP5?vjFZ_IzTub1_bKxm;y)_=_?F3g(}Y-g|Hy1B@x$!0pU)qR{#=>uB!A0hxlY#MU;diR_0UC4izU8;_(yx@OTKZ~KMcE%_^a~wVw@?P63i9-HU0J@e%cV!yTv|={_G5_vq<j(s69aZA?=W-CA=xdaoR27U!RNn<Qg##^;_B3`*e}}X`e3hF#IcdZqD|Ub)7X!;%{dig9a{?I?Y-l@!oCl9%l)-eF*tyt(EwEM-lQck3;<%SxItVy4W%A+S~;6@5<UQ{S5w8_W3Dapq{N+R_UkDRP^r*Zg3QJm~9ik=x#A|LG2>+mz^!XZ5igp8Gjq^A4c|h8Mo8#vd@nTmG`6UYcg)vFOiRP#w>Z>X5SLO;|au@BCDf6Q%;%mAG#LL8^dV45pg*`h#y`H>&-d7Z8qj3r{-n&-HPSCWx5yEwI!#X_%jkqE6%4Yr!#z`<9>P14SO>W<K}jg`0f#flF#U5^piV6;_H8GN8WQ+(f615Uw*@Tt0|&}JkN8-OMIIM**_ONis!zTw^-sEe1U#kesi!dnevuOe1o=Gh+nuN1;=^YCBDsc>1XDZeDQaP{~#XwsVhXjKm6riD?5hxMJedVl7Ei=6UPz1yf97t_r#xEXD9L)8HxL2<bNRk$Im0)y6`UYH}WrtZya8X`Le{y_Y=og;(PZ&eOn`MV}3M8nfOo7OF;iVU1c9|G`u4HJSOWg=&IDUqlx&}FJfGM&Orx0cQhAYPnw4H^}-x^FLtyNUn}a3eurNzmHs=3KPBxoT<_xBm<O%ETl^*8uR%Qp>^UTUAMwNbZO3@A+p(YM1;dzUPl+G$3)YvVV5ImnuOVKa_&fG7Ye9hcrlj%E$On>t!6fnT-IM2?|3>+~SP&`x`LKhi=djQ4T+<5Yi@&BR>fSYZ81@gXFiQNWpq+?c>Rlr73&cN{asa;X$W6Gvg&V|o<%Z(EhF!=LKT-Tw-msznk;mk|7j6;%v+G#@uF<KePix^0@$c4@{6~$lSLJIHqt@cO3Xh2Y{f3hj*PW>-Rs0LBG4Hy6-ez+}|Dyqi;fJ?!NPMaIH!sQcPkb~R`4_z<{;!Ae{mC-o5BXkNbWZ#&gYf(_nY+n;SaeDJZ%?BxU4Fal;$Nm;DD~?1?P^?C(P!*`O6o)T7nd>r6x=U;><B#P_2LKOuX}*!h4#{B+!t$cldCx1Jx|^nW(Q+`GKyP@pD5>RmSNcM^%7nD&GqE@J*&2S&np=w{u*!e@0?hOc``~yihtnaTxgtYvG~5?ABxD6Iv<67(peHL{_)NE6|c)x5+(lYFJpeSefliSQ^^AHcRhfwkN*|>lgSw`{=T*tR}Wl%w8a0RUzhxQtuFegzWa{4TV2gViwLRk(~>fAyQx+Gv^1;NfA!N+&t5(M-=CJ|xO3R)Zu6-7$n(exs7J^P$P1~*$P3BQ)T88RawPQtIg&h^`Z{?w`9*3H`9<<%>IU*;@&xKD<O$?))OfPeMdWd0bsq;%r%@M?r;(?#DPBsACo5e=o=y#6Q@n(_ioArJz@~T|buD=vc`J1zc`NxKbqDz%*+$(@wvn@`$I02`d}<mwpIksqCl`<%)Ks#AoJBoB&LU?}t>g^yN$M`L((UAv<il)=cT+c$mA*#aP2R?)cs+FuS?O}}dU70fCOM8A<8D)_LDZRKr8CGu<Vn;B@+9&^YB+f!IglDg4kQOqL&*VTf2xJ-Paeyrcr<l7c{JIF8ba>rZiC&;n;J~^CO=1wB0onSNL@i5NFGFel{|>-OHCyEl3$?iA-_PLPfaGzC%;6slV2jQq~?%Ul3%9gkzXbo)LgPbUgmD&-L1E~&7$@rEA3C7MUG`tyqc<$SCcnUN0F62Pu@h{!lrmHbqZPOT=HJ>AvVP+)Wzf!awc^dc^R)!vAWkoG^qg}@@VQ%t-NLwkEIUN%4<xqKXtfPUWbYUs3WxUx>X!V9jTSqx#EdbKdpRSD4s+eqm{2C#cG{RrH-eLA&=+1naZX(h8jzbA;(cyYvt=*@p|eet$cq_yp6g=E8klb@22k6%J(0|hpC6O^1Vy(NotB#zP~BXpk`|2d!ynkYOYqkmnwGf-i7df4kiavmym<WQPc!-6nO=89eD-$Rq9sqtK>xLL2@E_57kEALr$h<latAIYChRc&Y>2NbI5sA2id`SP~6wu`ncP(Y>K<HDfXiFBG+`czqwl-HpO+R4as%Mk5HSEA0aoRwjehnw`5cN7_}8yX*=>`<hE>zJ5Zk>cOZABdXhVnpQLspKS}nYb|*jXZmr$T<Ze&9+f(lL44dK})Gp*6<gV0?<gVmSR1>)qxjnTtxjnfJn_~59Tuqa|TGSfkTIBlFdgS`##?(gS#^mNy53&cxYEFHeT%BXrrq&|YCO4qgCpREBp*AKrAwNoOPHxVz6xZZ<s;2z?s#W)>@t^+XT>fWZVk-Uvy7HM1f1Rj!<}`O-e|@>|_p7C@$(=xTc~Mstru_@CNJfY'

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
